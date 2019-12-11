# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from datetime import datetime, date, time
from dateutil import relativedelta
from odoo.addons import decimal_precision as dp
from pytz import timezone
from odoo.addons.jekdoo.utils.util import Util
from odoo.exceptions import ValidationError


class HRPayslipFilter(models.TransientModel):
    _name = "hr.payslip.report"
    _description = 'Filter HR Payslip'

    period_id = fields.Many2one('berdikari.hr.attendance.period', string='Period Name', required=True)

    format_report = fields.Selection([
        ('karyawan_tetap', 'Laporan Rekapitulasi Gaji Karyawan Tetap'),
        ('karyawan_kontrak', 'Laporan Rekapitulasi Gaji Karyawan Kontrak'),
        ('direksi', 'Laporan Rekapitulasi Gaji Direksi'),
        ('penjaga', 'Laporan Rekapitulasi Gaji Penjaga'),
    ], required=True)

    @api.depends('period_id')
    @api.onchange('period_id')
    def onchange_domain_seq(self):
        domain = {}
        period_id = self.period_id.id
        if period_id:
            domain_seq = [('attendance_period_id', '=', period_id)]
            domain['period_seq_id'] = domain_seq
        hasil = {'domain': domain}
        return hasil

    period_seq_id = fields.Many2one('berdikari.hr.attendance.period.line', string='Period Sequence'
                                    # , required=True
                                    )

    @api.depends('period_seq_id')
    @api.onchange('period_seq_id')
    def onchange_period_seq(self):
        for rec in self:
            period_seq_id = rec.period_seq_id.id
            model_period_line = self.env['berdikari.hr.attendance.period.line']
            if period_seq_id:
                period_line = model_period_line.search([('id', '=', period_seq_id)], limit=1)
                rec.date_from = period_line.date_from
                rec.date_to = period_line.date_to

    date_from = fields.Date(string='Date From', readonly=True, default=False)
    # default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_to = fields.Date(string='Date To', readonly=True, default=False)
    # default=lambda self: fields.Date.to_string(
    #     (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid), required=True)

    struct_id = fields.Many2one('hr.payroll.structure', string='Structure', required=True)

    @api.multi
    def confirm_button(self):
        docs = {}
        format_report = self.format_report
        period_id = self.period_id
        period_seq_id = self.period_seq_id
        operating_unit_id = self.operating_unit_id
        struct_id = self.struct_id
        # ids = [1, 2]

        domain = [('operating_unit_id', '=', operating_unit_id.id),('struct_id', '=', struct_id.id), ]
        if period_id:
            domain.append(('period_id', '=', period_id.id))

        if period_seq_id:
            domain.append(('period_seq_id', '=', period_seq_id.id))

        payslip_ids = self.env['hr.payslip'].search(domain)
        ids = payslip_ids.ids

        setup = self.env['jekdoo.setup'].get_setup()
        gaji_pokok_id = setup.gaji_pokok_id
        tunjangan_perumahan_id = setup.tunjangan_perumahan_id
        tunjangan_transport_id = setup.tunjangan_transport_id
        bpjs_naker_perusahaan_id = setup.bpjs_naker_perusahaan_id
        bpjs_naker_pegawai_id = setup.bpjs_naker_pegawai_id
        potongan_bpjs_kesehatan_perusahaan_id = setup.potongan_bpjs_kesehatan_perusahaan_id
        potongan_bpjs_kesehatan_pegawai_id = setup.potongan_bpjs_kesehatan_pegawai_id
        tunjangan_jabatan_id = setup.tunjangan_jabatan_id
        potongan_pinjaman_id = setup.potongan_pinjaman_id

        for one in payslip_ids:
            employee_id = one.employee_id
            employee_id_id = employee_id.id

            gaji_pokok = 0
            tunjangan_jabatan = 0
            potongan_pinjaman = 0
            tunjangan_perumahan = 0
            tunjangan_transport = 0
            bpjs_naker_perusahaan = 0
            bpjs_naker_pegawai = 0
            potongan_bpjs_kesehatan_perusahaan = 0
            potongan_bpjs_kesehatan_pegawai = 0
            for line in one.line_ids:
                salary_rule_id_id = line.salary_rule_id.id

                if salary_rule_id_id == gaji_pokok_id.id:
                    gaji_pokok += line.total

                if salary_rule_id_id == tunjangan_jabatan_id.id:
                    tunjangan_jabatan += line.total

                if salary_rule_id_id == potongan_pinjaman_id.id:
                    potongan_pinjaman += line.total

                if format_report == 'direksi':
                    if salary_rule_id_id == tunjangan_perumahan_id.id:
                        tunjangan_perumahan += line.total

                    if salary_rule_id_id == tunjangan_transport_id.id:
                        tunjangan_transport += line.total

                if salary_rule_id_id == bpjs_naker_perusahaan_id.id:
                    bpjs_naker_perusahaan += line.total

                if salary_rule_id_id == bpjs_naker_pegawai_id.id:
                    bpjs_naker_pegawai += line.total

                if salary_rule_id_id == potongan_bpjs_kesehatan_perusahaan_id.id:
                    potongan_bpjs_kesehatan_perusahaan += line.total

                if salary_rule_id_id == potongan_bpjs_kesehatan_pegawai_id.id:
                    potongan_bpjs_kesehatan_pegawai += line.total

            bpjs_naker_total = bpjs_naker_perusahaan + bpjs_naker_pegawai
            potongan_bpjs_kesehatan_total = potongan_bpjs_kesehatan_perusahaan + potongan_bpjs_kesehatan_pegawai

            total_diterima = 0
            total_diterima += gaji_pokok
            if format_report != 'penjaga':
                total_diterima += gaji_pokok
                total_diterima += tunjangan_jabatan
                total_diterima += potongan_pinjaman
                total_diterima += tunjangan_perumahan
                total_diterima += tunjangan_transport
                total_diterima -= bpjs_naker_total
                total_diterima -= potongan_bpjs_kesehatan_total

            total_spp = 0
            satu = {}
            satu['id'] = one.id
            satu['name'] = employee_id.name
            satu['employee_id'] = employee_id_id
            currency_id = self.env.ref('base.IDR')[0]
            satu['currency_id'] = currency_id
            # import ipdb; ipdb.set_trace()
            if employee_id_id in docs:
                dua = docs[employee_id_id]

                satu['gaji_pokok'] = dua['gaji_pokok'] + gaji_pokok
                satu['tunjangan_jabatan'] = dua['tunjangan_jabatan'] + tunjangan_jabatan
                satu['potongan_pinjaman'] = dua['potongan_pinjaman'] + potongan_pinjaman
                satu['tunjangan_perumahan'] = dua['tunjangan_perumahan'] + tunjangan_perumahan
                satu['tunjangan_transport'] = dua['tunjangan_transport'] + tunjangan_transport
                satu['bpjs_naker_perusahaan'] = dua['bpjs_naker_perusahaan'] + bpjs_naker_perusahaan
                satu['bpjs_naker_pegawai'] = dua['bpjs_naker_pegawai'] + bpjs_naker_pegawai
                satu['bpjs_naker_total'] = dua['bpjs_naker_total'] + bpjs_naker_total
                satu['potongan_bpjs_kesehatan_perusahaan'] = dua['potongan_bpjs_kesehatan_perusahaan'] + potongan_bpjs_kesehatan_perusahaan
                satu['potongan_bpjs_kesehatan_pegawai'] = dua['potongan_bpjs_kesehatan_pegawai'] + potongan_bpjs_kesehatan_pegawai
                satu['potongan_bpjs_kesehatan_total'] = dua['potongan_bpjs_kesehatan_total'] + potongan_bpjs_kesehatan_total
                satu['total_diterima'] = dua['total_diterima'] + total_diterima
                satu['total_spp'] = dua['total_spp'] + total_spp
            else:
                satu['gaji_pokok'] = gaji_pokok
                satu['tunjangan_jabatan'] = tunjangan_jabatan
                satu['potongan_pinjaman'] = potongan_pinjaman
                satu['tunjangan_perumahan'] = tunjangan_perumahan
                satu['tunjangan_transport'] = tunjangan_transport
                satu['bpjs_naker_perusahaan'] = bpjs_naker_perusahaan
                satu['bpjs_naker_pegawai'] = bpjs_naker_pegawai
                satu['bpjs_naker_total'] = bpjs_naker_total
                satu['potongan_bpjs_kesehatan_perusahaan'] = potongan_bpjs_kesehatan_perusahaan
                satu['potongan_bpjs_kesehatan_pegawai'] = potongan_bpjs_kesehatan_pegawai
                satu['potongan_bpjs_kesehatan_total'] = potongan_bpjs_kesehatan_total
                satu['total_diterima'] = total_diterima
                satu['total_spp'] = total_spp

            docs[employee_id_id] = satu

        title = ''
        if format_report == 'direksi':
            report_name = 'berdikari.report_payslip_karyawan_direksi'
            title = 'Laporan Rekapitulasi Gaji Direksi / Komisaris'
        elif format_report == 'karyawan_tetap' or format_report == 'karyawan_kontrak' :
            report_name = 'berdikari.report_payslip_karyawan'
            if format_report == 'karyawan_tetap':
                title = 'Laporan Rekapitulasi Gaji Karyawan - Tetap'
            else:
                title = 'Laporan Rekapitulasi Gaji Karyawan - Kontrak'

        elif format_report == 'penjaga':
            report_name = 'berdikari.report_payslip_penjaga'
            title = 'Laporan Rekapitulasi Gaji Penjaga'
        else:
            return Util.jek_pop1('Belum di set untuk Format Report Tersebut')

        params = {'date_start': 123, 'model': docs, 'title': title, 'docs': payslip_ids}
        rep = self.env.ref(report_name)
        ret = rep.with_context(landscape=True).report_action(ids, data=params)
        return ret