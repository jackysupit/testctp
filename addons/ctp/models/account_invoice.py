# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.jekdoo.utils.util import Util
from odoo.exceptions import ValidationError, UserError
import json
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, \
    pycompat, date_utils

from num2words import num2words

# from datetime import datetime

import datetime
import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    _description = 'Inherit Account Invoice'

    partner_type = fields.Selection(selection=([('person','Individual'),('company','Company')]), related='partner_id.company_type')
    is_certificate_of_withholding_tax_released = fields.Boolean(string='Sent VAT Slip')
    is_ppn_count = fields.Boolean(string='VAT Calculated')
    is_ppn_credited = fields.Boolean(string='VAT Can be Credited')
    is_ppn_paid = fields.Boolean(string='Paid')
    tax_date = fields.Date(string='Tax Date')
    date_due2 = fields.Date(string='date_due Date')

    @api.onchange('date_due2')
    def onchange_date_due2(self):
        for rec in self:
            rec.date_due = rec.date_due2

    # partner_id = fields.Many2one('res.partner',string='Partner')
    vat = fields.Char(related='partner_id.vat',string='NPWP (Tax ID)')#get record from other model

    nego_rate = fields.Boolean(string='Rate Nego')
    rate = fields.Float(string='Rate')

    audit_period = fields.Boolean(string='Audit Period')
    certificate_of_withholding_tax_link = fields.Char(string='VAT Slip')

    # for CreditNotes
    calculated = fields.Boolean(string='VAT Calculated')
    vat_type = fields.Many2one('account.tax')
    vat_number = fields.Char(string='VAT Number')
    vat_date = fields.Date(string='VAT Date')
    file_vat = fields.Binary(string='VAT Slip', attachment=True)
    file_vat_name = fields.Char(string='File VAT Name')

    # for refund
    send_tax_slip = fields.Boolean(string='Send Tax Slip')

    # for cash advance and down payment
    # settle_type = fields.Selection(selection=([('cash_advance', 'Cash Advance'),('down_payment', 'Down Payment'),('cash advance', 'Cash Advance - Depreceated'),('down payment', 'Down Payment - Depreceated'),('cash-advance', 'Cash Advance - Depreceated'),('down-payment', 'Down Payment - Depreceated')]), store=True)
    settle_type = fields.Selection(selection=([('cash_advance', 'Cash Advance'),('down_payment', 'Down Payment')]), store=True)
    for_settle_id = fields.Many2one('account.invoice', store=True, domain="[('partner_id', '=', partner_id), ('for_settle_id', '=', False), ('state', '=', 'paid')]")
    amount = fields.Monetary(related='for_settle_id.amount_total', store=True, readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verified_document', 'Verified Document'),
        ('tax_validate', 'Tax Validate'),
        ('open', 'Open'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='Status', index=True, readonly=True, default='draft',
        track_visibility='onchange', copy=False,
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             " * The 'Open' status is used when user creates invoice, an invoice number is generated. It stays in the open status till the user pays the invoice.\n"
             " * The 'In Payment' status is used when payments have been registered for the entirety of the invoice in a journal configured to post entries at bank reconciliation only, and some of them haven't been reconciled with a bank statement line yet.\n"
             " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             " * The 'Cancelled' status is used when user cancel invoice.")

    def _readonly_trans_type(self):
        is_readonly = False

        if hasattr(self, '_context'):
            ctx = self._context
            if 'is_employee_transaction' in ctx and ctx.get('is_employee_transaction'):
                is_readonly = True
        return is_readonly

    def compute_is_employee_bill(self):
        for rec in self:
            if hasattr(self, '_context'):
                ctx = self._context
                rec.is_employee_bill = 'is_employee_bill' in ctx and ctx.get('is_employee_transaction')
    is_employee_bill = fields.Boolean(compute=compute_is_employee_bill)

    trans_type = fields.Selection(selection=([('bill', 'Bill'),('cash_advance', 'Cash Advance'),('down_payment', 'Down Payment'),('cash advance', 'Cash Advance - Depreceated'),('down payment', 'Down Payment - Depreceated')]), store=True, readonly=_readonly_trans_type)


    trans_type_cust = fields.Selection(selection=([('invoice', 'Invoice'),('sales-down-payment', 'Sales Down Payment')]),default='invoice', string='Trans Type')
    cash_advance_warning = fields.Date() #visible jika mode of payment Cash Advance
    ops_non_ops_id = fields.Many2one('berdikari.operational.non.operational', string='Ops./Non Ops. Activity')
    identification_number = fields.Char(string='Identification ID')
    is_pkp = fields.Boolean(string='PKP')
    vandor_id = fields.Many2one('res.partner')      #apa ini????
    original_bill_number = fields.Char()
    vat_collected_bill = fields.Char()
    farm_id = fields.Many2one('operating.unit', string='Unit')

    @api.depends('partner_id')
    @api.onchange('partner_id')
    def onchange_partner_id2(self):
        for rec in self:
            if rec.partner_id and rec.partner_id.employee_id and rec.partner_id.employee_id.department_id:
                rec.department_id = rec.partner_id.employee_id.department_id
            else:
                rec.department_id = False

    department_id = fields.Many2one('hr.department', string='Department')


    def _default_purchase_order_id(self):
        active_model = self._context.get('active_model')
        if active_model == 'purchase.order':
            active_id = self._context.get('active_id')
        else:
            active_id = False
        return active_id

    def _default_sale_order_id(self):
        active_model = self._context.get('active_model')
        if active_model == 'sale.order':
            active_id = self._context.get('active_id')
        else:
            active_id = False
        return active_id

    def _default_unit_id(self):
        active_model = self._context.get('active_model')
        operating_unit_id = False
        if active_model == 'purchase.order':
            active_id = self._context.get('active_id')

            model = self.env[active_model].sudo()
            rec = model.search([('id', '=', active_id)])
            if rec :
                 operating_unit_id = rec.operating_unit_id.id
        elif active_model == 'sale.order':
            active_id = self._context.get('active_id')

            model = self.env[active_model].sudo()
            rec = model.search([('id', '=', active_id)])
            if rec:
                operating_unit_id = rec.operating_unit_id.id
        return operating_unit_id

    purchase_order_id = fields.Many2one('purchase.order', default=_default_purchase_order_id)
    sale_order_id = fields.Many2one('sale.order', default=_default_sale_order_id)
    mode_of_payment_id = fields.Many2one('berdikari.mode.of.payment', related='sale_order_id.mode_of_payment_id')

    operating_unit_id = fields.Many2one('operating.unit', default=_default_unit_id, string=" Unit")
    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)



    warehouse_id = fields.Many2one('stock.warehouse', related="sale_order_id.warehouse_id", store=True)
    operational_id = fields.Many2one('berdikari.operational.non.operational', store=True, string='Verifikasi')
    tax_validation_user_id = fields.Many2one('res.users')

    def compute_is_hide_verified_doc(self):
        for rec in self:
            is_hide = True
            if rec.state == 'draft' \
                    and self.env.ref('account.group_account_invoice').id in self.env.user.groups_id.ids:
                is_hide = False
            rec.is_hide_verified_doc = is_hide
    is_hide_verified_doc = fields.Boolean(compute=compute_is_hide_verified_doc)

    def compute_is_hide_tax_validate(self):
        for rec in self:
            is_hide = True
            if rec.state == 'verified_document' \
                    and self.env.ref('berdikari.group_inventory_tax_validation').id in self.env.user.groups_id.ids:
                is_hide = False
            rec.is_hide_tax_validate = is_hide
    is_hide_tax_validate = fields.Boolean(compute=compute_is_hide_tax_validate)

    def compute_is_hide_dh_tax_approve(self):
        for rec in self:
            is_hide = True
            is_punya_hak = False
            user_id = rec.tax_validation_user_id
            employee_id = user_id.employee_id
            parent_id = employee_id.parent_id
            user_parent_id = parent_id.user_id
            if user_parent_id.id == self.env.user.id:
                is_punya_hak = True
            if rec.state == 'tax_validate' and is_punya_hak:
                is_hide = False
            rec.is_hide_dh_tax_approve = is_hide
    is_hide_dh_tax_approve = fields.Boolean(compute=compute_is_hide_dh_tax_approve)

    def compute_is_amount_gt_max_bill(self):
        for rec in self:
            vendor_id = rec.partner_id
            untax_amount = rec.amount_untaxed
            hasil = False
            for vendor in vendor_id:
                max_bill = vendor.maximal_bill
                hasil = untax_amount > max_bill  # 11 harusnya warning, tidak menghambat proses
            rec.is_amount_gt_max_bill = hasil
    is_amount_gt_max_bill = fields.Boolean(compute=compute_is_amount_gt_max_bill)


    def compute_is_ppn_gt_one_million(self):
        for rec in self:
            tax_amount = rec.amount_tax
            hasil = False
            for account in rec.invoice_line_ids:
                account = account.account_id
                ppn_material = False
                if account.is_tax_pph_account:
                    ppn_material = True
                hasil = tax_amount > 1000000 and ppn_material   #5 tree nya jd merah
            rec.is_ppn_gt_one_million = hasil
    is_ppn_gt_one_million = fields.Boolean(compute=compute_is_ppn_gt_one_million)


    def compute_is_npwp(self):
        for rec in self:
            vendor_id = rec.partner_id
            hasil = False
            npwp = False
            tax_material = False
            for vendor in vendor_id:
                npwp = vendor.vat
            for account in rec.invoice_line_ids:
                account = account.account_id
                if account.is_tax_pph_account or account.is_pph_credited or account.is_tax_ppn_account:
                    tax_material = True
            if not npwp and tax_material:
                hasil = True        #10 harusnya warning saja, tidak menghambat proses
            rec.is_npwp = hasil
    is_npwp = fields.Boolean(compute=compute_is_npwp)

    # untuk vendor bill
    def compute_validate_status(self):
        status_all = 0
        for rec in self:
            status = status_all #Nggak perlu Validate
            if rec.state == 'draft':
                if not rec.is_account_in_budget and not rec.is_amount_gt_max_bill and not rec.is_npwp:
                    status = 4 #Validate tanpa warning
                else:
                    if rec.is_account_in_budget:
                        status = 10 #validate is_account_in_budget
                        if rec.is_amount_gt_max_bill and not rec.is_npwp:
                            status = 3 #validate max bill
                        elif not rec.is_amount_gt_max_bill and rec.is_npwp:
                            status = 3 #validate npwp
                        elif rec.is_amount_gt_max_bill and rec.is_npwp:
                            status = 3 #validate npwp
                    else:
                        if rec.is_amount_gt_max_bill and not rec.is_npwp:
                            status = 1 #validate max bill
                        elif not rec.is_amount_gt_max_bill and rec.is_npwp:
                            status = 2 #validate npwp

            rec.validate_status = status

    validate_status = fields.Integer(compute=compute_validate_status)



    @api.multi
    def action_verified_doc(self):
        for satu in self:
            vendor_id = satu.partner_id
            trans_type = satu.trans_type
            trans_type_cust = satu.trans_type_cust
            date_invoice = satu.date_invoice
            satu.is_account_in_budget = False
            if satu.type == 'in_invoice':
                untax_amount = satu.amount_untaxed
                tax_amount = satu.amount_tax
                for vendor in vendor_id:
                    credit_limit = vendor.credit_limit
                    max_bill = vendor.maximal_bill
                    if trans_type == 'cash_advance':
                        doc = satu.env['account.invoice'].search([('partner_id', '=', vendor.id),('state', '=', 'open'),('trans_type', '=', 'cash_advance')])
                        count_doc = len(doc)
                        # if count_doc > 0:   #7
                        #     raise ValidationError(_('Silakan selesaikan transaksi yang tertunda'))
                        if untax_amount > credit_limit:       #8
                            raise ValidationError(_('Jumlah yang harus dibayarkan sebelum pajak lebih besar dari credit limit'))

                count = len(satu.invoice_line_ids)
                for rec in satu.invoice_line_ids:
                    flock_id = rec.flock_id.id
                    account = rec.account_id
                    coa_code = account.code
                    coa_name = account.name
                    coa_type_cash_advance = account.is_cash_advance
                    coa_type_down_payment = account.is_down_payment
                    coa_type_budget = account.is_budget_need_to_check
                    flock = rec.account_id.is_flock_mandatory
                    tax_material = False
                    ppn_material = False
                    if account.is_tax_pph_account or account.is_pph_credited or account.is_tax_ppn_account:
                        tax_material = True
                    if account.is_tax_pph_account:
                        ppn_material = True
                    if trans_type == 'cash_advance':
                        if count > 2:   #1
                            raise ValidationError(_('Trans Type Cash Advance dan detail lebih dari dua baris'))
                        if coa_type_cash_advance == False:  #2
                            raise ValidationError(_('Trans Type pada account harus cash advance juga'))
                    if trans_type == 'down_payment':
                        if count > 2:   #3
                            raise ValidationError(_('Trans Type Down Payment dan detail lebih dari dua baris'))
                        if coa_type_down_payment == False:  #4
                            raise ValidationError(_('Trans Type pada account harus down payment juga'))
                    if flock == True and flock_id == False:     #6
                        raise ValidationError(_('Flock harus di isi'))
                    if coa_type_budget:
                        total_theoritical_amount = 0
                        for budget in satu.env['crossovered.budget'].search(
                                [('date_from', '<=', date_invoice), ('date_to', '>=', date_invoice), ]):
                            id = budget.id
                            date_from = budget.date_from
                            date_to = budget.date_to
                            TODAY_CHECK = date_invoice

                            for line in budget.crossovered_budget_line:
                                crossovered_budget_id = line.crossovered_budget_id
                                general_budget_id = line.general_budget_id
                                general_budget_name = general_budget_id.name
                                theoritical_amount = line.theoritical_amount
                                if account.id in general_budget_id.account_ids.ids:
                                    total_theoritical_amount = total_theoritical_amount + theoritical_amount
                                if rec.price_subtotal > total_theoritical_amount:
                                    satu.is_account_in_budget = True
    
            elif satu.type == 'out_invoice':
                if trans_type_cust == 'sales-down-payment':
                    count = len(satu.invoice_line_ids)
                    if count > 2:  # 1
                        raise ValidationError(_('Trans Type Sales Down Payment dan detail lebih dari dua baris'))
                    for rec in satu.invoice_line_ids:
                        flock_id = rec.flock_id.id
                        flock = rec.account_id.is_flock_mandatory
                        account = rec.account_id
                        coa_type_sales_down_payment = account.is_sales_down_payment
                        coa_type_budget = account.is_budget_need_to_check
                        if coa_type_sales_down_payment == False:  #2
                            raise ValidationError(_('Trans Type pada account harus sales down payment juga'))
                        if flock == True and flock_id == False:  # 3
                            raise ValidationError(_('Flock harus di isi'))
                        if coa_type_budget:
                            total_theoritical_amount = 0
                            for budget in satu.env['crossovered.budget'].search(
                                    [('date_from', '<=', date_invoice), ('date_to', '>=', date_invoice), ]):
                                id = budget.id
                                date_from = budget.date_from
                                date_to = budget.date_to
                                TODAY_CHECK = date_invoice

                                for line in budget.crossovered_budget_line:
                                    crossovered_budget_id = line.crossovered_budget_id
                                    general_budget_id = line.general_budget_id
                                    general_budget_name = general_budget_id.name
                                    theoritical_amount = line.theoritical_amount
                                    if account.id in general_budget_id.account_ids.ids:
                                        total_theoritical_amount = total_theoritical_amount + theoritical_amount
                                        if rec.price_subtotal > total_theoritical_amount:
                                            satu.is_account_in_budget = True

            self.state = 'verified_document'
            # setiap mau push harus di aktifkan
            # return super(AccountInvoice, self).action_invoice_open()


    def action_tax_validate(self):
        self.tax_validation_user_id = self.env.user.id
        self.state = 'tax_validate'

    @api.multi
    def action_invoice_open(self):
        # lots of duplicate calls to action_invoice_open, so we remove those already open
        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: not inv.partner_id):
            raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
        if to_open_invoices.filtered(lambda inv: inv.state not in ('draft', 'tax_validate')):
            raise UserError(_("Invoice must be in draft state in order to validate it."))
        if to_open_invoices.filtered(
                lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
            raise UserError(_(
                "You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
        if to_open_invoices.filtered(lambda inv: not inv.account_id):
            raise UserError(
                _('No account was found to create the invoice, be sure you have installed a chart of account.'))
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        return to_open_invoices.invoice_validate()


    @api.multi
    def invoice_validate(self):
        ret = super(AccountInvoice, self).invoice_validate()

        print('Do something here after validate')
        for rec in self:
            for line in rec.invoice_line_ids:

                product_product_id = line.product_id
                if not product_product_id.is_flock_material:
                    continue

                setup = self.env['jekdoo.setup'].get_setup()

                journal_id = setup.journal_bills_validate_id
                if not journal_id:
                    raise ValidationError(_('Bills Validated Journal is not set in Custom Setup'))

                journal_name = journal_id.name

                debit_account_id = journal_id.default_debit_account_id
                credit_account_id = journal_id.default_credit_account_id

                if not debit_account_id:
                    raise ValidationError(
                        _('Default Debit Account for {} is not set in Custom Setup'.format(journal_name)))

                if not credit_account_id:
                    raise ValidationError(
                        _('Default Credit Account for {} is not set in Custom Setup'.format(journal_name)))

                qty = line.quantity
                standard_price = product_product_id.standard_price
                value = qty * standard_price

                if not standard_price:
                    raise ValidationError(
                        _('Cost Price is not set for product: {}'.format(product_product_id.display_name)))
                    # continue

                if not qty:
                    continue

                satu = {
                    'account_id': journal_id.id,
                    'operating_unit_id': rec.operating_unit_id.id,
                    # 'flock_id': rec.flock_id.id,
                    # 'currency_id': rec.currency_id.id,
                }

                satu_debit = satu.copy()
                satu_debit['account_id'] = debit_account_id.id
                satu_debit['debit'] = value

                satu_credit = satu.copy()
                satu_credit['account_id'] = credit_account_id.id
                satu_credit['credit'] = value

                flock_id = rec.purchase_order_id.flock_id

                vals_move = {
                    'date': rec.date,
                    # 'account_invoice_id': rec.id,
                    # 'purchase_order_id': rec.purchase_order_id,
                    'operating_unit_id': rec.operating_unit_id.id,
                    'journal_id': journal_id.id,
                    'flock_id': flock_id.id,
                    'journal_type': 'BILL_VALIDATED',
                    'line_ids': [
                        (0, 0, satu_debit),
                        (0, 0, satu_credit)
                    ],
                }
                move = self.env['account.move']
                rec_move = move.create(vals_move)

                rec_move.post()

        return ret

    @api.onchange('invoice_line_ids', 'date_invoice')
    def onchange_line_ids2(self):
        for satu in self:
            vendor_id = satu.partner_id
            trans_type = satu.trans_type
            trans_type_cust = satu.trans_type_cust
            date_invoice = satu.date_invoice

            satu.is_account_in_budget = False

            count = len(satu.invoice_line_ids)
            for rec in satu.invoice_line_ids:
                flock_id = rec.flock_id.id
                account = rec.account_id
                coa_code = account.code
                coa_name = account.name
                coa_type_cash_advance = account.is_cash_advance
                coa_type_down_payment = account.is_down_payment
                coa_type_budget = account.is_budget_need_to_check
                flock = rec.account_id.is_flock_mandatory
                tax_material = False
                ppn_material = False

                if coa_type_budget:
                    total_theoritical_amount = 0
                    budget_ids = satu.env['crossovered.budget'].search(
                            [('date_from', '<=', date_invoice), ('date_to', '>=', date_invoice), ])
                    for budget in budget_ids:
                        id = budget.id
                        date_from = budget.date_from
                        date_to = budget.date_to
                        TODAY_CHECK = date_invoice

                        for line in budget.crossovered_budget_line:
                            crossovered_budget_id = line.crossovered_budget_id
                            general_budget_id = line.general_budget_id
                            general_budget_name = general_budget_id.name
                            theoritical_amount = line.theoritical_amount
                            if account.id in general_budget_id.account_ids.ids:
                                total_theoritical_amount = total_theoritical_amount + theoritical_amount

                                if rec.price_subtotal > total_theoritical_amount:
                                    satu.is_account_in_budget = True


    is_account_in_budget = fields.Boolean(compute=onchange_line_ids2)
    total_theoritical_amount = fields.Float(compute=onchange_line_ids2)

    @api.one
    def _get_outstanding_info_JSON(self):
        self.outstanding_credits_debits_widget = json.dumps(False)
        if self.state == 'open':
            domain = ['|',
                      ('account_id', '=', self.account_id.id),
                      '|',
                      ('account_id', '=', self.env['res.partner']._find_accounting_partner(
                          self.partner_id).property_account_receivable_for_down_payment_id.id),
                      ('account_id', '=', self.env['res.partner']._find_accounting_partner(
                          self.partner_id).property_account_payable_for_down_payment_id.id),
                      ('partner_id', '=', self.env['res.partner']._find_accounting_partner(self.partner_id).id),
                      ('reconciled', '=', False),
                      '|',
                      '&', ('amount_residual_currency', '!=', 0.0), ('currency_id', '!=', None),
                      '&', ('amount_residual_currency', '=', 0.0), '&', ('currency_id', '=', None),
                      ('amount_residual', '!=', 0.0)]
            if self.type in ('out_invoice', 'in_refund'):
                domain.extend([('credit', '>', 0), ('debit', '=', 0)])
                type_payment = _('Outstanding credits')
            else:
                domain.extend([('credit', '=', 0), ('debit', '>', 0)])
                type_payment = _('Outstanding debits')
            info = {'title': '', 'outstanding': True, 'content': [], 'invoice_id': self.id}
            lines = self.env['account.move.line'].search(domain)
            currency_id = self.currency_id
            if len(lines) != 0:
                for line in lines:
                    # get the outstanding residual value in invoice currency
                    if line.currency_id and line.currency_id == self.currency_id:
                        amount_to_show = abs(line.amount_residual_currency)
                    else:
                        currency = line.company_id.currency_id
                        amount_to_show = currency._convert(abs(line.amount_residual), self.currency_id, self.company_id,
                                                           line.date or fields.Date.today())
                    if float_is_zero(amount_to_show, precision_rounding=self.currency_id.rounding):
                        continue
                    if line.ref:
                        title = '%s : %s' % (line.move_id.name, line.ref)
                    else:
                        title = line.move_id.name
                    info['content'].append({
                        'journal_name': line.ref or line.move_id.name,
                        'title': title,
                        'amount': amount_to_show,
                        'currency': currency_id.symbol,
                        'id': line.id,
                        'position': currency_id.position,
                        'digits': [69, self.currency_id.decimal_places],
                    })
                info['title'] = type_payment
                self.outstanding_credits_debits_widget = json.dumps(info)
                self.has_outstanding = True

    def compute_amount_word(self):
        for rec in self:
            if rec.amount_total:
                amount_in_word = num2words(int(rec.amount_total), lang='id')
                rec.amount_in_word = amount_in_word.title() + ' Rupiah'
    amount_in_word = fields.Char(compute=compute_amount_word)

    @api.onchange('currency_id')
    def compute_current_rate(self):
        for rec in self:
            rec.current_rate = rec.currency_id.with_context(dict(self._context or {}, date=rec.date_invoice)).rate
    current_rate = fields.Float(compute=compute_current_rate, store=True)


class CustomersInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    _description = 'Inherit Account Invoice Line'

    flock_id = fields.Many2one('berdikari.flock.master')

    total_theoritical_amount = fields.Float()

    current_rate = fields.Float(related='invoice_id.current_rate')