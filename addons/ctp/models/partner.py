# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = 'res.partner'
    _description = 'Inherit Res Partner'

    is_pkp = fields.Boolean(string='Taxable Company')

    # name = fields.Char(index=True)
    # _sql_constraints = [('name_unique', 'UNIQUE (name)', 'Name must be unique.')]

    @api.depends('employee_id')
    @api.onchange('employee_id')
    def compute_employee_id(self):
        for rec in self:
            rec.employee = bool(rec.employee_id)

    credit_limit = fields.Monetary(currency_field='currency_id', string='Credit Limit', store=True, compute=compute_employee_id)
    file_npwp = fields.Binary(string='File NPWP', attachment=True)
    file_npwp_name = fields.Char(string='File NPWP Name')
    file_siup = fields.Binary(string='File SIUP', attachment=True)
    file_siup_name = fields.Char(string='File SIUP Name')
    file_tdp = fields.Binary(string='File TDP', attachment=True)
    file_tdp_name = fields.Char(string='File TDP Name')
    file_akta_perusahaan = fields.Binary(string='File Akta Perusahaan', attachment=True)
    file_akta_perusahaan_name = fields.Char(string='File Akta Perusahaan Name')
    file_ktp_owner = fields.Binary(string='File KTP Owner', attachment=True)
    file_ktp_owner_name = fields.Char(string='File KTP Ownew Name')
    file_others = fields.Binary(string='File Others', attachment=True)
    file_others_name = fields.Char(string='File Others Name')
    document_type_id = fields.Many2one('berdikari.document.type')
    institution_id = fields.Many2one('berdikari.institution.type', string='Institution Type')
    maximal_bill = fields.Monetary(currency_field='currency_id', store=True)
    product_category_id = fields.Many2one('product.category')
    identification_number = fields.Char()
    is_limit_check = fields.Boolean(string='Limit Check')
    property_account_payable_for_down_payment_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Payable For Down Payment",
        # domain="[('internal_type', '=', 'payable'), ('deprecated', '=', False)]",
        required=True)
    property_account_receivable_for_down_payment_id = fields.Many2one('account.account', company_dependent=True,
        string="Account Receivable For Down Payment",
        # domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False)]",
        required=True)

    doc_partner_ids = fields.One2many('berdikari.res.partner.document', 'partner_id')

    employee_id = fields.Many2one('hr.employee', string='Employee')

    def compute_show_address(self):
        for rec in self:
            name = rec._display_address(without_company=True)
            rec.str_show_address = name
    str_show_address = fields.Text(compute=compute_show_address)

    @api.multi
    def _compute_total_ap(self):
        for rec in self:
            model_account_invoice = self.env['account.invoice']
            my_ap = model_account_invoice.search([
                ('type', '=', 'in_invoice'),
                ('partner_id', '=', rec.id),
                ('state', '=', 'open'),
            ])

            total_ap = 0
            for one in my_ap:
                total_ap += one.residual_signed

            rec.total_ap = total_ap

    total_ap = fields.Monetary('Total AP', compute=_compute_total_ap)
    # bill_ids = fields.Many2many('account.invoice', 'partner_account_invoice_rel', 'partner_id', 'id',
    #                             string='Vendor Bills',
    #                             domain="[('type','=','in_invoice'),('state','=','open')]")

    # bill_ids = fields.One2many('partner.account.invoice', 'partner_id')

    @api.multi
    def _compute_total_ar(self):
        for rec in self:
            model_account_invoice = self.env['account.invoice']
            my_ap = model_account_invoice.search([
                ('type', '=', 'out_invoice'),
                ('partner_id', '=', rec.id),
                ('state', '=', 'open'),
            ])

            total = 0
            for one in my_ap:
                total += one.residual_signed

            rec.total_ar = total

    total_ar = fields.Monetary('Total AR', compute=_compute_total_ar)
    tax_validation_user_id = fields.Many2one('res.users')
    # employee_id = fields.Many2one('hr.employee', related='tax_validation_user_id.employee_id')
    # parent_id = fields.Many2one('hr.employee', string='Manager', related='employee_id.parent_id')
    # user_parent_id = fields.Many2one('res.users', string='Manager', related='parent_id.user_id')
    # invoice_ids = fields.Many2many('account.invoice', 'partner_account_invoice_rel', 'partner_id', 'id',
    #                             string='Vendor Bills',
    #                             domain="[('type','=','out_invoice'),('state','=','open')]")
    approval_state = fields.Selection(selection=[('draft', 'Draft'), ('sales_comfirm', 'Sales Confirm'), ('dh_sales_approve', 'DH Sales Approve'),
                                        ('tax_validation', 'Tax Validation'), ('dh_tax_approve', 'DH Tax Approve')], default='draft')
    active = fields.Boolean(default=False)
    is_contact = fields.Boolean(default=False)

    is_confirm = fields.Boolean(default=False)
    is_dept_head_approve = fields.Boolean(default=False)
    is_tax_validation = fields.Boolean(default=False)
    is_dh_tax_approve = fields.Boolean(default=False)

    product_ids = fields.One2many('product.supplierinfo', 'name', string='Products')

    def compute_is_hide_confirm(self):
        for rec in self:
            is_hide = True
            if rec.active:
                is_hide = True
            elif rec.is_confirm == False:
                is_hide = False
            rec.is_hide_confirm = is_hide

    is_hide_confirm = fields.Boolean(compute=compute_is_hide_confirm, default=True)

    def compute_is_hide_dept_head(self):
        for rec in self:
            is_hide = True
            if rec.active:
                is_hide = True
            else:
                group_dept_head_id = self.env.ref('berdikari.group_accounting_dept_head')
                is_punya_hak = group_dept_head_id.id in self.env.user.groups_id.ids
                if rec.is_confirm and is_punya_hak:
                    is_hide = False
                if rec.is_dept_head_approve and is_punya_hak:
                    is_hide = True
            rec.is_hide_dept_head = is_hide

    is_hide_dept_head = fields.Boolean(compute=compute_is_hide_dept_head, default=True)

    def compute_is_hide_tax(self):
        for rec in self:
            is_hide = True
            if rec.active:
                is_hide = True
            else:
                group_tax_id = self.env.ref('berdikari.group_inventory_tax_validation')
                is_punya_hak = group_tax_id.id in self.env.user.groups_id.ids
                if rec.is_confirm and rec.is_dept_head_approve and is_punya_hak:
                    is_hide = False
                if rec.is_tax_validation and is_punya_hak:
                    is_hide = True
            rec.is_hide_tax = is_hide

    is_hide_tax = fields.Boolean(compute=compute_is_hide_tax, default=True)

    def compute_is_hide_dh_tax(self):
        for rec in self:
            is_hide = True
            if rec.active:
                is_hide = True
            else:
                is_punya_hak = False
                user_id = rec.tax_validation_user_id
                employee_id = user_id.employee_id
                parent_id = employee_id.parent_id
                user_parent_id = parent_id.user_id
                if user_parent_id.id == self.env.user.id:
                    is_punya_hak = True
                if rec.is_confirm and rec.is_dept_head_approve and rec.is_tax_validation and is_punya_hak:
                    is_hide = False
                if rec.is_dh_tax_approve and is_punya_hak:
                    is_hide = True
            rec.is_hide_dh_tax = is_hide

    is_hide_dh_tax = fields.Boolean(compute=compute_is_hide_dh_tax, default=True)

    def action_confirm_vendor(self):
        self.is_confirm = True
        self.approval_state = 'sales_comfirm'

    def action_approve_dept_head(self):
        self.is_dept_head_approve = True
        self.approval_state = 'dh_sales_approve'

    def action_tax_validate(self):
        self.tax_validation_user_id = self.env.user.id
        self.is_tax_validation = True
        self.approval_state = 'tax_validation'

    def action_dh_tax_approve(self):
        self.is_dh_tax_approve = True
        self.approval_state = 'dh_tax_approve'
        self.active = True

    @api.model
    def create(self, vals):
        # asalnya approval hanya untuk vendor
        # vals['active'] = False
        # if vals.get('customer'):
        #     vals['active'] = True

        rec = super(Partner, self).create(vals)
        if 'employee_id' in vals and vals.get('employee_id'):
            rec.employee_id.user_id = rec.user_id

        return rec

    @api.multi
    def write(self, vals):
        if 'employee_id' in vals:
            for rec in self:
                if rec.employee_id and rec.employee_id.user_id:
                    rec.employee_id.user_id = False
                if rec.employee_id and rec.employee_id.partner_id:
                    rec.employee_id.partner_id = False

        result = super(Partner, self).write(vals)
        for rec in self:
            if 'employee_id' in vals and vals.get('employee_id'):
                rec.employee_id.partner_id = rec.id
                if rec.user_id:
                    rec.employee_id.user_id = rec.user_id

        return result

    @api.multi
    def copy(self, default=None):
        new_partner = super(Partner, self).copy(default=default)
        new_partner.write({
            'approval_state': 'draft',
            'is_confirm': False,
            'is_dept_head_approve': False,
            'is_tax_validation': False,
            'is_dh_tax_approve': False,
            'active': False,
        })
        return new_partner

    @api.constrains('vat')
    def _check_vat(self):
        for record in self:
            if record.company_type == "person":
                if record.vat == "":
                    raise Warning(_("TAX ID Blank"))

class PartnerDocument(models.Model):
    _name = 'berdikari.res.partner.document'
    _description = 'Berdikari Res Partner Document'

    partner_id = fields.Many2one('res.partner')
    document_name = fields.Char()
    expired_date = fields.Date()
    legal_id = fields.Char(string='Legal ID')
    location = fields.Char()
    attached_doc = fields.Binary(string='Attached Doc', attachment=True)
    attached_doc_name = fields.Char(string='Attached Doc Name')
    document_type = fields.Char()
    warning_date = fields.Date()
