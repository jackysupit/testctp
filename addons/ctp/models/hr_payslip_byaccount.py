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


class HRPayslipByAccount(models.TransientModel):
    _name = "hr.payslip.byaccount"
    _description = 'Filter HR Payslip By Account'

    period_id = fields.Many2one('berdikari.hr.attendance.period', string='Period Name', required=True)

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

    @api.multi
    def confirm_button(self):
        docs = {}
        period_id = self.period_id
        period_seq_id = self.period_seq_id
        operating_unit_id = self.operating_unit_id
        # ids = [1, 2]

        domain = [('operating_unit_id', '=', operating_unit_id.id),('state', '=', 'done'),]
        if period_id:
            domain.append(('period_id', '=', period_id.id))

        if period_seq_id:
            domain.append(('period_seq_id', '=', period_seq_id.id))

        payslip_ids = self.env['hr.payslip'].search(domain)
        ids = payslip_ids.ids

        print('################# domain: ', domain)
        print('################# payslip_ids: ', payslip_ids)

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

        karyawan_tetap_id = setup.karyawan_tetap_id
        karyawan_tetap_id_id = setup.karyawan_tetap_id.id
        karyawan_kontrak_id = setup.karyawan_kontrak_id
        karyawan_kontrak_id_id = setup.karyawan_kontrak_id.id
        direksi_id = setup.direksi_id
        direksi_id_id = setup.direksi_id.id

        if not karyawan_tetap_id:
            raise ValidationError(_('Karyawan Tetap is not set up in Configuration'))
        if not karyawan_kontrak_id:
            raise ValidationError(_('Karyawan Kontrak is not set up in Configuration'))
        if not direksi_id:
            raise ValidationError(_('Direksi is not set up in Configuration'))

        list_docs = {}
        for one in payslip_ids:
            for line in one.line_ids:

                index_nama = 0
                index_karyawan_tetap = 1
                index_karyawan_kontrak = 2
                index_direksi = 3
                index_total = 4

                salary_rule_id = line.salary_rule_id
                salary_rule_id_id = salary_rule_id.id
                salary_rule_id_name = salary_rule_id.name
                gaji = line.total
                if salary_rule_id_id in list_docs:
                    gaji_satu = list_docs[salary_rule_id_id]
                else:
                    gaji_satu = [salary_rule_id_name, 0, 0, 0, 0]

                if karyawan_tetap_id_id == one.struct_id.id:
                    gaji_satu[index_karyawan_tetap] += gaji
                elif karyawan_kontrak_id_id == one.struct_id.id:
                    gaji_satu[index_karyawan_kontrak] += gaji
                elif direksi_id_id == one.struct_id.id:
                    gaji_satu[index_direksi] += gaji

                total = 0
                total += gaji_satu[index_karyawan_tetap]
                total += gaji_satu[index_karyawan_kontrak]
                total += gaji_satu[index_direksi]
                gaji_satu[index_total] = total
                list_docs[salary_rule_id_id] = gaji_satu

            total_diterima = 0
            # total_diterima += gaji_pokok
            # total_diterima += gaji_pokok
            # total_diterima += tunjangan_jabatan
            # total_diterima += potongan_pinjaman
            # total_diterima += tunjangan_perumahan
            # total_diterima += tunjangan_transport
            # total_diterima -= bpjs_naker_total
            # total_diterima -= potongan_bpjs_kesehatan_total

            total_spp = 0
            satu = {}
            satu['id'] = one.id
            satu['name'] = 'NAME'
            satu['total_diterima'] = total_diterima
            satu['total_spp'] = total_spp

        print('####################################### AAAAAAAAAAAAAAAAA list_docs: ', list_docs)

        report_name = 'berdikari.report_payslip_byaccount'
        title = 'Laporan Rekapitulasi Gaji Berdasarkan Account'

        params = {'title': title, 'docs': list_docs, 'list_docs': list_docs}
        rep = self.env.ref(report_name)
        ret = rep.with_context(landscape=True).report_action(payslip_ids, data=params)
        return ret