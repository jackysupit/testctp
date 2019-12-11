# -*- coding: utf-8 -*-

from odoo.tools.safe_eval import safe_eval

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.jekdoo.utils.util import Util

from datetime import datetime, date

import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Inherit Account Move'

    sale_order_id = fields.Many2one('sale.order')
    purchase_order_id = fields.Many2one('purchase.order')
    account_invoice_id = fields.Many2one('account.invoice', string='Customer Invoice / Vendor Bill')

    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)
    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)

    flock_id = fields.Many2one('berdikari.flock.master', string='Flock ID')
    journal_type = fields.Selection([('PENYUSUTAN','PENYUSUTAN ASSET'), ('KEMATIAN','KEMATIAN ASSET'), ('ASSET_RECEIPT','ASSET RECEIPT'), ('BILL_VALIDATED','BILL VALIDATED'), ('PAYMENT_VALIDATED','PAYMENT VALIDATED'), ('general', 'Miscellaneous')])


    #hi vinny

    @api.model
    def create(self, vals):
        amount_total = 0
        line_ids = vals.get('line_ids')
        if line_ids:
            for line in line_ids:
                one = line[2]
                if one.get('debit'):
                    amount_total += one.get('debit')

        ctx = self._context
        active_model = ctx.get('active_model')
        active_id = ctx.get('active_id')
        create_bill = ctx.get('create_bill')

        if active_model == 'purchase.order':
            model = self.env[active_model]
            rec = model.search([('id', '=', active_id)])

            if rec:
                vals['operating_unit_id'] = rec.operating_unit_id.id
                vals['purchase_order_id'] = active_id

                ai = self.env['account.invoice'].search([('purchase_order_id', '=', active_id)], order='id desc', limit=1)
                if ai and ai.amount_total == amount_total:
                    vals['account_invoice_id'] = ai.id
        elif active_model == 'sale.order':
            model = self.env[active_model]
            rec = model.search([('id', '=', active_id)])

            if rec:
                vals['operating_unit_id'] = rec.operating_unit_id.id
                vals['sale_order_id'] = active_id

                line_ids = vals.get('line_ids')
                if line_ids:
                    line = line_ids[0]
                    if len(line) >= 2:
                        line_row = line[2]
                        if line_row:
                            invoice_id = line_row.get('invoice_id')
                            if invoice_id:
                                vals['account_invoice_id'] = invoice_id
                else:
                    ai = self.env['account.invoice'].search([('sale_order_id', '=', active_id)], order='id desc', limit=1)
                    if ai and ai.amount_total == amount_total:
                        vals['account_invoice_id'] = ai.id
        else:
            active_id = ctx.get('id') or ctx.get('active_id')
            the_model = ctx.get('model')
            active_model = ctx.get('active_model')
            if active_id and the_model == 'sale.order' and active_model == 'sale.advance.payment.inv':
                model = self.env[the_model]
                rec = model.search([('id', '=', active_id)])

                if rec:
                    vals['operating_unit_id'] = rec.operating_unit_id.id
                    vals['sale_order_id'] = active_id

                    line_ids = vals.get('line_ids')
                    if line_ids:
                        line = line_ids[0]
                        if len(line) >= 2:
                            line_row = line[2]
                            if line_row:
                                invoice_id = line_row.get('invoice_id')
                                if invoice_id:
                                    vals['account_invoice_id'] = invoice_id
                    else:
                        ai = self.env['account.invoice'].search([('sale_order_id', '=', active_id)], order='id desc', limit=1)
                        if ai and ai.amount_total == amount_total:
                            vals['account_invoice_id'] = ai.id

        ret = super(AccountMove, self).create(vals)
        return ret

    @api.multi
    def post(self, invoice=False):
        if invoice:
            for move in self:
                move.account_invoice_id = invoice.id
        # return super(AccountMove, self).post(invoice=invoice)     #diganti karena error invoice
        return super(AccountMove, self).post()

    # untuk mengakomodasi down payment
    @api.constrains('line_ids', 'journal_id', 'auto_reverse', 'reverse_date')
    def _validate_move_modification(self):
        type = self.mapped('line_ids.payment_id.payment_type')
        if 'posted' in self.mapped('line_ids.payment_id.state'):
            if 'inbound_down_payment' not in type:
                if 'outbound_down_payment' not in type:
                    raise ValidationError(_("You cannot modify a journal entry linked to a posted payment."))

    # untuk mengakomodasi down payment
    @api.multi
    def assert_balanced(self):
        if not self.ids:
            return True
        prec = self.env.user.company_id.currency_id.decimal_places

        self._cr.execute("""\
                SELECT      move_id
                FROM        account_move_line
                WHERE       move_id in %s
                GROUP BY    move_id
                HAVING      abs(sum(debit) - sum(credit)) > %s
                """, (tuple(self.ids), 10 ** (-max(5, prec))))
        type = self.mapped('line_ids.payment_id.payment_type')
        if len(self._cr.fetchall()) != 0:
            if 'inbound_down_payment' not in type:
                if 'outbound_down_payment' not in type:
                    raise ValidationError(_("You cannot modify a journal entry linked to a posted payment."))
            # if not 'inbound_down_payment' or 'outbound_down_payment' in self.mapped('line_ids.payment_id.payment_type'):
            #     raise UserError(_("Cannot create unbalanced journal entry."))
        return True

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _query_get(self, domain=None):
        self.check_access_rights('read')

        context = dict(self._context or {})
        domain = domain or []
        if not isinstance(domain, (list, tuple)):
            domain = safe_eval(domain)

        date_field = 'date'
        if context.get('aged_balance'):
            date_field = 'date_maturity'
        if context.get('date_to'):
            domain += [(date_field, '<=', context['date_to'])]
        if context.get('date_from'):
            if not context.get('strict_range'):
                domain += ['|', (date_field, '>=', context['date_from']),
                           ('account_id.user_type_id.include_initial_balance', '=', True)]
            elif context.get('initial_bal'):
                domain += [(date_field, '<', context['date_from'])]
            else:
                domain += [(date_field, '>=', context['date_from'])]

        if context.get('journal_ids'):
            domain += [('journal_id', 'in', context['journal_ids'])]

        if context.get('operating_unit_ids'):
            domain += [('operating_unit_id', 'in', context['operating_unit_ids'])]

        state = context.get('state')
        if state and state.lower() != 'all':
            domain += [('move_id.state', '=', state)]

        if context.get('company_id'):
            domain += [('company_id', '=', context['company_id'])]

        if 'company_ids' in context:
            domain += [('company_id', 'in', context['company_ids'])]

        if context.get('reconcile_date'):
            domain += ['|', ('reconciled', '=', False), '|', ('matched_debit_ids.max_date', '>', context['reconcile_date']),
                       ('matched_credit_ids.max_date', '>', context['reconcile_date'])]

        if context.get('account_tag_ids'):
            domain += [('account_id.tag_ids', 'in', context['account_tag_ids'].ids)]

        if context.get('account_ids'):
            domain += [('account_id', 'in', context['account_ids'].ids)]

        if context.get('analytic_tag_ids'):
            domain += [('analytic_tag_ids', 'in', context['analytic_tag_ids'].ids)]

        if context.get('analytic_account_ids'):
            domain += [('analytic_account_id', 'in', context['analytic_account_ids'].ids)]

        if context.get('partner_ids'):
            domain += [('partner_id', 'in', context['partner_ids'].ids)]

        if context.get('partner_categories'):
            domain += [('partner_id.category_id', 'in', context['partner_categories'].ids)]

        where_clause = ""
        where_clause_params = []
        tables = ''
        if domain:
            query = self._where_calc(domain)

            # Wrap the query with 'company_id IN (...)' to avoid bypassing company access rights.
            self._apply_ir_rules(query)

            tables, where_clause, where_clause_params = query.get_sql()
        return tables, where_clause, where_clause_params

    @api.multi
    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        # Empty self can happen if the user tries to reconcile entries which are already reconciled.
        # The calling method might have filtered out reconciled lines.
        if not self:
            return True

        self._check_reconcile_validity()
        # reconcile everything that can be
        remaining_moves = self.auto_reconcile_lines()

        writeoff_to_reconcile = self.env['account.move.line']
        # if writeoff_acc_id specified, then create write-off move with value the remaining amount from move in self
        if writeoff_acc_id and writeoff_journal_id and remaining_moves:
            all_aml_share_same_currency = all([x.currency_id == self[0].currency_id for x in self])
            writeoff_vals = {
                'account_id': writeoff_acc_id.id,
                'journal_id': writeoff_journal_id.id
            }
            if not all_aml_share_same_currency:
                writeoff_vals['amount_currency'] = False
            writeoff_to_reconcile = remaining_moves._create_writeoff([writeoff_vals])
            # add writeoff line to reconcile algorithm and finish the reconciliation
            remaining_moves = (remaining_moves + writeoff_to_reconcile).auto_reconcile_lines()
        # Check if reconciliation is total or needs an exchange rate entry to be created
        (self + writeoff_to_reconcile).check_full_reconcile()
        return True

    # untuk mengakomodasi down payment
    def _check_reconcile_validity(self):
        # Perform all checks on lines
        # import ipdb; ipdb.set_trace()
        company_ids = set()
        all_accounts = []
        all_move = []
        all_payment_type = []
        model_move = self.env['account.move']
        model_move_line = self.env['account.move.line']
        model_payment = self.env['account.payment']
        for line in self:
            all_move.append(line.move_id.id)
            company_ids.add(line.company_id.id)
            all_accounts.append(line.account_id)
            if (line.matched_debit_ids or line.matched_credit_ids) and line.reconciled:
                raise UserError(_('You are trying to reconcile some entries that are already reconciled.'))
        if len(company_ids) > 1:
            raise UserError(_('To reconcile the entries company should be the same for all entries.'))
        # if len(set(all_accounts)) > 1:
        #     raise UserError(_('Entries are not from the same account.'))
        if not (all_accounts[0].reconcile or all_accounts[0].internal_type == 'liquidity'):
            raise UserError(_(
                'Account %s (%s) does not allow reconciliation. First change the configuration of this account to allow it.') % (
                                all_accounts[0].name, all_accounts[0].code))
        if len(set(all_accounts)) > 1:
            move = model_move.search([('id', '=', all_move[1])], limit=1)
            move_line_ids = model_move_line.search([('move_id', '=', all_move[1])], limit=1)
            payment = model_payment.search([('move_name', '=', move.name)])
            payment_type = payment.payment_type
            if payment_type == 'inbound_down_payment' or payment_type == 'outbound_down_payment':
                # bikin journal pembayarannya
                for aml in move_line_ids:
                    vals = {
                        'name': aml.name,
                        'quantity': aml.quantity,
                        'product_uom_id': aml.quantity,
                        'product_id': aml.quantity,
                        'debit': move.amount if aml.debit == 0 else 0,
                        'credit': move.amount if aml.credit == 0 else 0,
                        'balance': (-1 * move.amount) if aml.debit > 0 else move.amount,
                        'debit_cash_basis': move.amount if aml.debit_cash_basis == 0 else 0,
                        'credit_cash_basis': move.amount if aml.credit_cash_basis == 0 else 0,
                        'balance_cash_basis': move.amount if aml.balance_cash_basis == 0 else 0,
                        'amount_currency': aml.amount_currency,
                        'company_currency_id': aml.company_currency_id.id,
                        'currency_id': aml.currency_id.id,
                        'amount_residual': (-1 * move.amount) if aml.amount_residual > 0 else move.amount,
                        'amount_residual_currency': aml.amount_residual_currency,
                        'tax_base_amount': aml.tax_base_amount,
                        'account_id': aml.account_id.id,
                        'move_id': aml.move_id.id,
                        'ref': aml.ref,
                        'payment_id': aml.payment_id.id,
                        'statement_line_id': aml.statement_line_id.id,
                        'statement_id': aml.statement_id.id,
                        'reconciled': aml.reconciled,
                        'full_reconcile_id': aml.full_reconcile_id.id,
                        'journal_id': aml.journal_id.id,
                        'blocked': aml.blocked,
                        'date_maturity': date.today(),
                        'date': date.today(),
                        'tax_line_id': aml.tax_line_id.id,
                        'analytic_account_id': aml.analytic_account_id.id,
                        'company_id': aml.company_id.id,
                        'invoice_id': aml.invoice_id.id,
                        'partner_id': aml.partner_id.id,
                        'user_type_id': aml.user_type_id.id,
                        'tax_exigible': aml.tax_exigible,
                        'created_uid': self.env.user.id,
                        'created_date': datetime.today(),
                        'write_uid': self.env.user.id,
                        'write_date': datetime.today(),
                        'expense_id': aml.expense_id.id,
                        'expected_pay_date': aml.expected_pay_date,
                        'internal_note': aml.internal_note,
                        'next_action_date': aml.next_action_date,
                        'flock_id': aml.flock_id,
                        'operating_unit_id': aml.operating_unit_id.id,
                    }
                    model_move_line.create(vals)

    @api.model
    def _compute_amount_fields(self, amount, src_currency, company_currency, nego_rate, rate):
        """ Helper function to compute value for fields debit/credit/amount_currency based on an amount and the currencies given in parameter
            di overwrite untuk kebutuhan nego rate
        """
        amount_currency = False
        currency_id = False
        date = self.env.context.get('date') or fields.Date.today()
        company = self.env.context.get('company_id')
        company = self.env['res.company'].browse(company) if company else self.env.user.company_id
        if src_currency and src_currency != company_currency:
            amount_currency = amount
            if not nego_rate:
                amount = src_currency._convert(amount, company_currency, company, date)
            amount = amount * rate
            currency_id = src_currency.id
        debit = amount > 0 and amount or 0.0
        credit = amount < 0 and -amount or 0.0
        return debit, credit, amount_currency, currency_id