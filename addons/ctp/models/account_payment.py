# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.jekdoo.utils.util import Util

from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class MyInvoices(models.Model):
    _name = 'account.payment.invoice'
    _description = 'Inherit Account Payment Invoice'

    account_payment_id = fields.Many2one('account.payment')

    partner_id = fields.Many2one('res.partner', related='account_payment_id.partner_id', store=True)

    @api.onchange('partner_id', 'account_payment_id')
    def domain_invoice_and_bill(self):
        domain = [('state','=','open')]

        if not self.partner_id:
            self.partner_id = self.account_payment_id.partner_id

        if self.partner_id:
            domain.append(('partner_id','=',self.partner_id.id))
        else:
            domain.append(('partner_id','=',0))

        domain_invoice_id = domain + [('type','=','out_invoice')]
        domain_bill_id = domain + [('type','=','in_invoice')]
        domain_all = {
            'domain': {
                'invoice_id': domain_invoice_id,
                'bill_id': domain_bill_id,
            }
        }
        return domain_all

    # partner_id = fields.Many2one('res.partner')
    # invoice_id = fields.Many2one('account.invoice')
    invoice_id = fields.Many2one('account.invoice')
    invoice_id_currency_id = fields.Many2one('res.currency', string='Currency', related='invoice_id.currency_id', store=True)
    invoice_id_number = fields.Char(string='Number', related='invoice_id.number', store=True)
    invoice_id_date_invoice = fields.Date(related='invoice_id.date_invoice')
    invoice_id_date_due = fields.Date(related='invoice_id.date_due')
    invoice_id_amount = fields.Monetary(related='invoice_id.residual_signed', currency_field='invoice_id_currency_id', store=True)

    # bill_id = fields.Many2one('account.invoice')
    bill_id = fields.Many2one('account.invoice')
    bill_id_number = fields.Char(string='Number', related='bill_id.number', store=True)
    bill_id_currency_id = fields.Many2one('res.currency', string='Currency', related='bill_id.currency_id', store=True)
    bill_id_date_invoice = fields.Date(related='bill_id.date_invoice')
    bill_id_date_due = fields.Date(related='bill_id.date_due')
    bill_id_amount = fields.Monetary(related='bill_id.residual_signed', currency_field='bill_id_currency_id', store=True)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    journal_type = fields.Selection([
            ('sale', 'Sale'),
            ('purchase', 'Purchase'),
            ('cash', 'Cash'),
            ('bank', 'Bank'),
            ('general', 'Miscellaneous'),
        ],
        help="Select 'Sale' for customer invoices journals.\n"\
        "Select 'Purchase' for vendor bills journals.\n"\
        "Select 'Cash' or 'Bank' for journals that are used in customer or vendor payments.\n"\
        "Select 'General' for miscellaneous operations journals.",
        related="journal_id.type", store=True
    )

    payment_type = fields.Selection(selection_add=[('inbound_down_payment', 'Receive Money For Down Payment'), ('outbound_down_payment', 'Send Money For Down Payment')])

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if not self.invoice_ids:
            # Set default partner type for the payment type
            if self.payment_type == 'inbound' or self.payment_type == 'inbound_down_payment':
                self.partner_type = 'customer'
            elif self.payment_type == 'outbound' or self.payment_type == 'outbound_down_payment':
                self.partner_type = 'supplier'
            else:
                self.partner_type = False
        # Set payment method domain
        res = self._onchange_journal()
        if not res.get('domain', {}):
            res['domain'] = {}
        jrnl_filters = self._compute_journal_domain_and_types()
        journal_types = jrnl_filters['journal_types']
        journal_types.update(['bank', 'cash'])
        res['domain']['journal_id'] = jrnl_filters['domain'] + [('type', 'in', list(journal_types))]
        return res

    @api.multi
    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconcilable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted."))

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
            # keep the name in case of a payment reset to draft
            if not rec.name:
                # Use the right sequence to set the name
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound' or rec.payment_type == 'inbound_down_payment':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound' or rec.payment_type == 'outbound_down_payment':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound' or rec.payment_type == 'inbound_down_payment':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound' or rec.payment_type == 'outbound_down_payment':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer', 'outbound_down_payment') and 1 or -1)
            move = rec._create_payment_entry(amount)

            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(
                    lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            rec.write({'state': 'posted', 'move_name': move.name})
        return True


    def _get_shared_move_line_vals(self, debit, credit, amount_currency, move_id, invoice_id=False):
        """ Returns values common to both move lines (except for debit, credit and amount_currency which are reversed)
        """
        return {
            'partner_id': self.payment_type in ('inbound', 'outbound', 'inbound_down_payment', 'outbound_down_payment') and self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
            'invoice_id': invoice_id and invoice_id.id or False,
            'move_id': move_id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency or False,
            'payment_id': self.id,
            'journal_id': self.journal_id.id,
        }

    def _get_counterpart_move_line_vals(self, invoice=False):
        if self.payment_type == 'transfer':
            name = self.name
        else:
            name = ''
            if self.partner_type == 'customer':
                if self.payment_type == 'inbound' or self.payment_type == 'inbound_down_payment':
                    name += _("Customer Payment")
                elif self.payment_type == 'outbound' or self.payment_type == 'outbound_down_payment':
                    name += _("Customer Credit Note")
            elif self.partner_type == 'supplier':
                if self.payment_type == 'inbound' or self.payment_type == 'inbound_down_payment':
                    name += _("Vendor Credit Note")
                elif self.payment_type == 'outbound' or self.payment_type == 'outbound_down_payment':
                    name += _("Vendor Payment")
            if invoice:
                name += ': '
                for inv in invoice:
                    if inv.move_id:
                        name += inv.number + ', '
                name = name[:len(name)-2]
        return {
            'name': name,
            'account_id': self.destination_account_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }

    def _get_liquidity_move_line_vals(self, amount):
        name = self.name
        if self.payment_type == 'transfer':
            name = _('Transfer to %s') % self.destination_journal_id.name

        default_debit_account_id = self.journal_id.default_debit_account_id.id
        default_credit_account_id = self.journal_id.default_credit_account_id.id

        # if self.payment_type == 'inbound_down_payment':
        #     default_credit_account_id = 2060

        vals = {
            'name': name,
            'account_id': self.payment_type in ('outbound','transfer', 'outbound_down_payment') and default_debit_account_id or default_credit_account_id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }
        print('################## account_id: ', self.payment_type in ('outbound','transfer', 'outbound_down_payment'))
        print('################## account_id: ', default_debit_account_id)
        print('################## account_id: ', default_credit_account_id)

        # If the journal has a currency specified, the journal item need to be expressed in this currency
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            amount = self.currency_id._convert(amount, self.journal_id.currency_id, self.company_id, self.payment_date or fields.Date.today())
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(date=self.payment_date)._compute_amount_fields(amount, self.journal_id.currency_id, self.company_id.currency_id,self.nego_rate,self.rate)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })
        return vals


    is_pay_with_ar = fields.Boolean('Pay with AR')
    @api.onchange('is_pay_with_ar', 'len_pay_invoice_ids')
    def on_change_is_pay_with_ar(self):
        if self.is_pay_with_ar:
            self.set_amount_ar()
        else:
            if self.payment_difference:
                self.amount = self.amount + self.payment_difference

    is_pay_with_ap = fields.Boolean('Pay with AP')
    @api.onchange('is_pay_with_ap', 'len_pay_bill_ids')
    def on_change_is_pay_with_ap(self):
        if self.is_pay_with_ap:
            self.set_amount_ap()
        else:
            if self.payment_difference:
                self.amount = self.amount + self.payment_difference

    def set_amount_ar(self):
        detail = self.pay_invoice_ids
        total = 0
        for one in detail:
            if one.id:
                total += one.residual_signed

        tagihan = self.amount + self.payment_difference
        if total > tagihan:
            bayar = tagihan
        else:
            if total:
                bayar = total
            else:
                bayar = tagihan

        self.amount = bayar

    def set_amount_ap(self):
        detail = self.pay_bill_ids
        total = 0
        for one in detail:
            if one.id:
                total += one.residual_signed

        tagihan = self.amount + self.payment_difference
        if total > tagihan:
            bayar = tagihan
        else:
            if total:
                bayar = total
            else:
                bayar = tagihan
        self.amount = bayar


    def _default_journal_id(self):
        model_account_journal = self.env['account.journal']
        rec = model_account_journal.search([('type', 'in', ['cash', 'bank'])], order='type desc, id asc', limit=1)
        ret = False
        if rec:
            ret = rec.id
        return ret

    journal_id = fields.Many2one('account.journal', string='Payment Journal',
                                 required=True,
                                 domain=[('type', 'in', ['cash', 'bank'])],
                                 default=_default_journal_id
                                 )

    @api.onchange('amount', 'currency_id', 'invoice_ids')
    def _onchange_amount(self):
        domain = [('type', 'in', ['cash', 'bank'])]
        journal_type = ''
        if self.invoice_ids:
            rec_invoice = self.invoice_ids[0]
            journal_type = rec_invoice.sale_order_id.mode_of_payment_id.journal_type
            if journal_type:
                domain = [('type', '=', journal_type)]

                model_account_journal = self.env['account.journal']
                rec = model_account_journal.search([('type', 'in', [journal_type])], order='type desc, id asc', limit=1)
                if rec:
                    self.journal_id = rec
        return {
            'domain': {
                'journal_id': domain,
            }
        }

    def action_validate_invoice_payment(self):
        ret = super(AccountPayment, self).action_validate_invoice_payment()

        model_invoice = self.env['account.invoice']
        model_account_payment = self.env['account.payment']
        # {'default_invoice_ids': [(4, active_id, None)]}
        # total = 0
        # x = 0
        # len_all = len(self.pay_invoice_ids)
        # for one in self.pay_invoice_ids:
        #     x += 1
        #     if x < len_all:
        #
        #     total += one.residual_signed

        my_invoice_number = self.communication
        settle_type = self.settle_type
        for_settle_id = self.for_settle_id

        # rec_invoice = model_invoice.browse(active_id)
        rec_invoice = self.invoice_ids
        rec_invoice.write({'settle_type': settle_type, 'for_settle_id': for_settle_id.id})

        # notes:
        # sengaja menggunakan query agar on write tidak dieksekusi
        #todo sementara doang diar tidak error
        if for_settle_id:
            logos = """
                update account_invoice set state='paid' where id={}
            """.format(for_settle_id.id)
            self.env.cr.execute(logos)

        list_rec_account_payment = []
        journal_id = self._default_journal_id()
        today = datetime.today().strftime('%Y-%m-%d')

        ############################################################################################################
        ##Payment Validate Journal - Start
        ############################################################################################################
        setup = self.env['jekdoo.setup'].get_setup()
        journal_id = setup.journal_payment_validate_id
        if not journal_id:
            raise ValidationError(_('Payment Validated Journal is not set in Custom Setup'))

        journal_name = journal_id.name

        debit_account_id = journal_id.default_debit_account_id
        credit_account_id = journal_id.default_credit_account_id

        if not debit_account_id:
            raise ValidationError(
                _('Default Debit Account for {} is not set in Custom Setup'.format(journal_name)))

        if not credit_account_id:
            raise ValidationError(
                _('Default Credit Account for {} is not set in Custom Setup'.format(journal_name)))

        currency = self.currency_id
        currency_idr = self.env['res.currency'].search([('name','=','IDR')], limit=1)
        amount = currency._convert(abs(self.amount), currency_idr, self.company_id, self.payment_date or fields.Date.today())

        value = amount

        satu = {
            'account_id': journal_id.id,
            'operating_unit_id': self.operating_unit_id.id,
            # 'flock_id': rec.flock_id.id,
            # 'currency_id': rec.currency_id.id,
        }

        satu_debit = satu.copy()
        satu_debit['account_id'] = debit_account_id.id
        satu_debit['debit'] = value

        satu_credit = satu.copy()
        satu_credit['account_id'] = credit_account_id.id
        satu_credit['credit'] = value

        flock_id = False
        if self.invoice_ids:
            if self.invoice_ids[0].purchase_order_id:
                flock_id = self.invoice_ids[0].purchase_order_id.flock_id

        flock_id_id = False
        if flock_id:
            flock_id_id = flock_id.id

        """
            # 'account_invoice_id': rec.id,
            # 'purchase_order_id': rec.purchase_order_id,
        """
        vals_move = {
            'date': self.payment_date,
            'operating_unit_id': self.operating_unit_id.id,
            'journal_id': journal_id.id,
            'flock_id': flock_id_id,
            'journal_type': 'PAYMENT_VALIDATED',
            'line_ids': [
                (0, 0, satu_debit),
                (0, 0, satu_credit)
            ],
        }
        move = self.env['account.move']
        rec_move = move.create(vals_move)

        rec_move.post()
        ############################################################################################################
        ##Payment Validate Journal - End
        ############################################################################################################


        for one in self.pay_invoice_ids:
            # one.write({'settle_type': settle_type, 'for_settle_id': for_settle_id})

            active_id = one.invoice_id.id
            amount = one.invoice_id.residual_signed
            currency_id = one.invoice_id.currency_id.id
            invoice_number = one.invoice_id.display_name
            partner_type = 'customer' if one.invoice_id.type == 'out_invoice' else 'supplier'
            partner_id = one.invoice_id.partner_id.id
            vals = {
                    'journal_id': journal_id,
                    # 'is_pay_with_ar': False,
                    # 'is_pay_with_ap': False,
                    'payment_method_id': 2,
                    'writeoff_label': 'Write-Off',
                    'payment_difference_handling': 'open',
                    'payment_type': 'outbound',
                    'payment_date': today,
                    'pay_invoice_ids': False,
                    'amount': amount,
                    'currency_id': currency_id,
                    'communication': invoice_number,
                    'partner_bank_account_id': False,
                    'payment_token_id': False,
                    'writeoff_account_id': False,
                    'payment_reference': 'paid with {}'.format(my_invoice_number),
                    'invoice_ids': [(6, 0, [active_id])],
                    'partner_type': partner_type,
                    'partner_id': partner_id,
                }
            rec_account_payment = model_account_payment.with_context({'active_ids': active_id}).create(vals)
            rec_account_payment.action_validate_invoice_payment()
            # one.invoice_id.action_invoice_paid()

            # rec_invoice = model_invoice.browse(active_id)
            # rec_invoice.write({'state': 'paid'})
            # rec_invoice.update({'state': 'paid'})
            # rec_invoice.state = 'paid'

            # notes:
            # sengaja menggunakan query agar on write tidak dieksekusi
            logos = """
                update account_invoice set state='paid' where id={}
            """.format(active_id)
            self.env.cr.execute(logos)

            # super(AccountPayment, rec_account_payment).action_validate_invoice_payment()
            list_rec_account_payment.append(rec_account_payment)

        if self.pay_invoice_ids:
            logos = 'paid with {}'
            csv_invoice = ''
            for one in self.pay_invoice_ids:
                invoice_number = one.invoice_id.display_name
                csv_invoice += ',' if csv_invoice else ''
                csv_invoice += invoice_number
            self.write({'payment_reference': logos.format(csv_invoice)})

        return ret




    # def _compute_partner_type(self):
    #     for rec in self:
    #         partner_type = rec.my_partner_type
    #         rec.my_partner_type = partner_type
    #
    # my_partner_type = fields.Char('Partner Type', compute = _compute_partner_type)
    total_ap = fields.Monetary('Total AP', related='partner_id.total_ap')
    total_ar = fields.Monetary('Total AR', related='partner_id.total_ar')

    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
            di overwrite untuk kebutuhan nego rate
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id,self.nego_rate,self.rate)

        move = self.env['account.move'].create(self._get_move_vals())

        #Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)
        #Reconcile with the invoices
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id,self.nego_rate,self.rate)
            writeoff_line['name'] = self.writeoff_label
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo

        #Write counterpart lines
        if not self.currency_id.is_zero(self.amount):
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0
            liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
            print('#################### liquidity_aml_dict before update: ', liquidity_aml_dict)
            liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
            print('#################### liquidity_aml_dict: ', liquidity_aml_dict)

            aml_obj.create(liquidity_aml_dict)

        #validate the payment
        if not self.journal_id.post_at_bank_rec:
            move.post()

        #reconcile the invoice receivable/payable line(s) with the payment
        if self.invoice_ids:
            self.invoice_ids.register_payment(counterpart_aml)
        return move

    def _compute_len_pay_invoice_ids(self):
        for rec in self:
            rec.len_pay_invoice_ids = len(rec.pay_invoice_ids) if rec.len_pay_invoice_ids else 0
    len_pay_invoice_ids = fields.Integer(compute=_compute_len_pay_invoice_ids)
    pay_invoice_ids = fields.One2many('account.payment.invoice', 'account_payment_id')

    def _compute_len_pay_bill_ids(self):
        for rec in self:
            rec.len_pay_bill_ids = len(rec.pay_bill_ids) if rec.pay_bill_ids else 0
    len_pay_bill_ids = fields.Integer(compute=_compute_len_pay_bill_ids)
    pay_bill_ids = fields.One2many('account.payment.invoice', 'account_payment_id')

    settle_type = fields.Selection(selection=([('cash_advance', 'Cash Advance'),('down_payment', 'Down Payment'), ('cash advance', 'Cash Advance Depreceated'), ('down payment', 'Down Payment Depreceated')]))
    for_settle_id = fields.Many2one('account.invoice', domain=[('state', '=', 'open')])

    @api.onchange('communication')
    def domain_for_settle_id(self):
        prefix = self.communication
        domain = {}
        domain['for_settle_id'] = [('state', '=', 'open'),
                                   ('partner_id', '=', self.partner_id.id)]

        if prefix:
            prefix = prefix.split('/')
            addPrefix = ('number', 'like', prefix[0])
            domain['for_settle_id'].append(addPrefix)

        return {
            'domain': domain
        }

    @api.onchange('for_settle_id')
    def change_amount(self):
        for_settle_id = self.for_settle_id
        if for_settle_id:
            self.amount = for_settle_id.residual
    # amount = fields.Monetary(currency_field='currency_id', store=True, string='Amount')

    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        if self.invoice_ids:
            self.destination_account_id = self.invoice_ids[0].account_id.id
        elif self.payment_type == 'transfer':
            if not self.company_id.transfer_account_id.id:
                raise UserError(_('There is no Transfer Account defined in the accounting settings. Please define one to be able to confirm this transfer.'))
            self.destination_account_id = self.company_id.transfer_account_id.id
        elif self.partner_id:
            if self.partner_type == 'customer':
                if self.payment_type == 'inbound_down_payment':
                    self.destination_account_id = self.partner_id.property_account_receivable_for_down_payment_id
                else:
                    self.destination_account_id = self.partner_id.property_account_receivable_id.id
            else:
                if self.payment_type == 'outbound_down_payment':
                    self.destination_account_id = self.partner_id.property_account_payable_for_down_payment_id
                else:
                    self.destination_account_id = self.partner_id.property_account_payable_id.id
        elif self.partner_type == 'customer':
            default_account = self.env['ir.property'].get('property_account_receivable_id', 'res.partner')
            self.destination_account_id = default_account.id
        elif self.partner_type == 'supplier':
            default_account = self.env['ir.property'].get('property_account_payable_id', 'res.partner')
            self.destination_account_id = default_account.id