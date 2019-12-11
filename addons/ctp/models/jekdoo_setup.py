# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero


class JeksooSetup(models.Model):
    _inherit = "jekdoo.setup"

    def _default_journal_kematian_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            default = row_setup.journal_kematian_id
        return default

    journal_kematian_id = fields.Many2one('account.journal', default=_default_journal_kematian_id,
                                          string="Death Asset Journal")

    def _default_journal_penyusutan_aset_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            default = row_setup.journal_penyusutan_aset_id
        return default

    journal_penyusutan_aset_id = fields.Many2one('account.journal', default=_default_journal_penyusutan_aset_id,
                                                 string="Asset Depreciation Journal")

    def _default_journal_asset_receipt_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            default = row_setup.journal_asset_receipt_id
        return default

    journal_asset_receipt_id = fields.Many2one('account.journal', default=_default_journal_asset_receipt_id,
                                                 string="Asset Receipt Journal")

    def _default_journal_asset_reclass_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            default = row_setup.journal_asset_reclass_id
        return default

    journal_asset_reclass_id = fields.Many2one('account.journal', default=_default_journal_asset_reclass_id,
                                                 string="Asset Reclass Journal")

    def _default_journal_bills_validate_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            default = row_setup.journal_bills_validate_id
        return default

    journal_bills_validate_id = fields.Many2one('account.journal', default=_default_journal_bills_validate_id,
                                                 string="Bills Validated Journal")

    def _default_journal_payment_validate_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            default = row_setup.journal_payment_validate_id
        return default

    journal_payment_validate_id = fields.Many2one('account.journal', default=_default_journal_payment_validate_id,
                                                 string="Payment Validated Journal")


    def _compute_is_user_biasa(self):
        for rec in self:
            user = self.env.user
            is_user_biasa = False
            if user:
                is_user_biasa = user.has_group('jekdoo.read_only_user')
                print('OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO is_user_biasa: ', is_user_biasa)
            rec.is_user_biasa = is_user_biasa

    is_user_biasa = fields.Boolean(compute=_compute_is_user_biasa)

    def _default_default_payment_term_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            default = row_setup.default_payment_term_id
        return default

    default_payment_term_id = fields.Many2one('account.payment.term', default=_default_default_payment_term_id)

    def _default_phase_pertama_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            default = row_setup.phase_pertama_id
        return default

    phase_pertama_id = fields.Many2one('berdikari.phase', default=_default_phase_pertama_id)

    def _default_phase_production_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            default = row_setup.phase_production_id
        return default

    phase_production_id = fields.Many2one('berdikari.phase', default=_default_phase_production_id)

    currency_id = fields.Many2one('res.currency', string='Currency', store=True)
    cash_advance_limit = fields.Monetary(currency_field='currency_id', store=True, default='1000000')
    due_days_for_cash_advance = fields.Integer(default=14)
    warning_days_before_due_date = fields.Integer(default=7)
    diff_limit = fields.Float(default=1.5, help='Batas mininal keterlambatan yang dihitung')

    def _default_foh_reserve_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            default = row_setup.foh_reserve_id
        return default

    foh_reserve_id = fields.Many2one('account.account', string='FOH Reserve', default=_default_foh_reserve_id)

    def _default_intermediate_account_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            default = row_setup.intermediate_account_id
        return default

    intermediate_account_id = fields.Many2one('account.account', default=_default_intermediate_account_id)

    def _default_cogs_manufacture_account_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            default = row_setup.cogs_manufacture_account_id
        return default

    cogs_manufacture_account_id = fields.Many2one('account.account', string='COGS Manufacture Account',
                                                  default=_default_cogs_manufacture_account_id)

    # Biasakan, relational fields/many2one itu harus pakai _id

    def _default_asset_account_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            default = row_setup.asset_account_id
        return default

    asset_account_id = fields.Many2one('account.account', string='Asset Account', default=_default_asset_account_id)

    def _default_prefix_akun_biaya(self):
        default = '61'
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            default = row_setup.prefix_akun_biaya
        return default

    prefix_akun_biaya = fields.Char(default=_default_prefix_akun_biaya)

    def _default_wip_account_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            default = row_setup.wip_account_id
        return default

    wip_account_id = fields.Many2one('account.account', string='WIP Account', default=_default_wip_account_id)

    def _default_produk_jadi_account_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            default = row_setup.produk_jadi_account_id
        return default

    produk_jadi_account_id = fields.Many2one('account.account', string='Produk Jadi Account',
                                             default=_default_produk_jadi_account_id)

    def _default_department_keuangan_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            if hasattr(row_setup, 'dept_keuangan_id'):
                default = row_setup.dept_keuangan_id
        return default

    dept_keuangan_id = fields.Many2one('hr.department', string='Dept Keuangan', default=_default_department_keuangan_id)

    def _default_job_dept_head_keuangan_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            if hasattr(row_setup, 'job_dept_head_keuangan_id'):
                default = row_setup.job_dept_head_keuangan_id
        return default

    job_dept_head_keuangan_id = fields.Many2one('hr.job', string='Job Dept Head',
                                                default=_default_job_dept_head_keuangan_id)

    def _default_department_akuntansi_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            if hasattr(row_setup, 'dept_akuntansi_id'):
                default = row_setup.dept_akuntansi_id
        return default

    dept_akuntansi_id = fields.Many2one('hr.department', string='Dept Akuntansi',
                                        default=_default_department_akuntansi_id)

    def _default_job_dept_head_akuntansi_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            if hasattr(row_setup, 'job_dept_head_akuntansi_id'):
                default = row_setup.job_dept_head_akuntansi_id
        return default

    job_dept_head_akuntansi_id = fields.Many2one('hr.job', string='Job Dept Head',
                                                 default=_default_job_dept_head_akuntansi_id)

    def _default_dept_head_hr_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            if hasattr(row_setup, 'dept_head_hr_id'):
                default = row_setup.dept_head_hr_id
        return default

    dept_head_hr_id = fields.Many2one('hr.employee', string='HR Dept Head',
                                                 default=_default_dept_head_hr_id)

    def _default_gaji_pokok_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            if hasattr(row_setup, 'gaji_pokok_id'):
                default = row_setup.gaji_pokok_id
        return default

    gaji_pokok_id = fields.Many2one('hr.salary.rule', default=_default_gaji_pokok_id)

    def _default_tunjangan_perumahan_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            if hasattr(row_setup, 'tunjangan_perumahan_id'):
                default = row_setup.tunjangan_perumahan_id
        return default
    tunjangan_perumahan_id = fields.Many2one('hr.salary.rule', default=_default_tunjangan_perumahan_id)

    def _default_tunjangan_transport_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            if hasattr(row_setup, 'tunjangan_transport_id'):
                default = row_setup.tunjangan_transport_id
        return default
    tunjangan_transport_id = fields.Many2one('hr.salary.rule', default=_default_tunjangan_transport_id)

    def _default_bpjs_naker_perusahaan_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            if hasattr(row_setup, 'bpjs_naker_perusahaan_id'):
                default = row_setup.bpjs_naker_perusahaan_id
        return default
    bpjs_naker_perusahaan_id = fields.Many2one('hr.salary.rule', default=_default_bpjs_naker_perusahaan_id)

    def _default_bpjs_naker_pegawai_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            if hasattr(row_setup, 'bpjs_naker_pegawai_id'):
                default = row_setup.bpjs_naker_pegawai_id
        return default
    bpjs_naker_pegawai_id = fields.Many2one('hr.salary.rule', default=_default_bpjs_naker_pegawai_id)

    def _default_potongan_bpjs_kesehatan_perusahaan_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            if hasattr(row_setup, 'potongan_bpjs_kesehatan_perusahaan_id'):
                default = row_setup.potongan_bpjs_kesehatan_perusahaan_id
        return default
    potongan_bpjs_kesehatan_perusahaan_id = fields.Many2one('hr.salary.rule', default=_default_potongan_bpjs_kesehatan_perusahaan_id)

    def _default_potongan_bpjs_kesehatan_pegawai_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            if hasattr(row_setup, 'potongan_bpjs_kesehatan_pegawai_id'):
                default = row_setup.potongan_bpjs_kesehatan_pegawai_id
        return default
    potongan_bpjs_kesehatan_pegawai_id = fields.Many2one('hr.salary.rule', default=_default_potongan_bpjs_kesehatan_pegawai_id)

    #  Tunjangan Jabatan,
    #  Potongan Pinjaman,
    #  Total Potongan,
    #  BPJS Naker(Perusahaan),
    #  BPJS Naker(Pegawai),
    #  Total Potongan BPJS Naker,
    #  THP,
    #  Maks BPJS Kesehatan,
    #  BPJS Kesehatan(Perusahaan),
    #  BPJS Kesehatan(Pegawai),
    #  Total Potongan BPJS Kesehatan,
    #  Total Diterima
    def _default_tunjangan_jabatan_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            if hasattr(row_setup, 'tunjangan_jabatan_id'):
                default = row_setup.tunjangan_jabatan_id
        return default
    tunjangan_jabatan_id = fields.Many2one('hr.salary.rule', default=_default_tunjangan_jabatan_id)

    def _default_potongan_pinjaman_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            if hasattr(row_setup, 'potongan_pinjaman_id'):
                default = row_setup.potongan_pinjaman_id
        return default
    potongan_pinjaman_id = fields.Many2one('hr.salary.rule', default=_default_potongan_pinjaman_id)


    def _default_karyawan_tetap_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            if hasattr(row_setup, 'karyawan_tetap_id'):
                default = row_setup.karyawan_tetap_id
        return default
    karyawan_tetap_id = fields.Many2one('hr.payroll.structure', default=_default_karyawan_tetap_id)

    def _default_karyawan_kontrak_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            if hasattr(row_setup, 'karyawan_kontrak_id'):
                default = row_setup.karyawan_kontrak_id
        return default
    karyawan_kontrak_id = fields.Many2one('hr.payroll.structure', default=_default_karyawan_kontrak_id)

    def _default_direksi_id(self):
        default = False
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            if hasattr(row_setup, 'direksi_id'):
                default = row_setup.direksi_id
        return default
    direksi_id = fields.Many2one('hr.payroll.structure', default=_default_direksi_id)

