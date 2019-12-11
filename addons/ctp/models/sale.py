# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo.addons.jekdoo.utils.util import Util


class Sale(models.Model):
    _inherit = "sale.order"
    _description = 'Sale Order'


    def default_unit_id(self):
        return self.env.user.operating_unit_id


    mode_of_payment_id = fields.Many2one('berdikari.mode.of.payment')

    def default_payment_term_id(self):
        setup = Util.get_setup(self)
        return setup.default_payment_term_id

    def domain_payment_term_id(self):
        term15 = self.env.ref('account.account_payment_term_15days').id
        term30 = self.env.ref('account.account_payment_term_net').id
        domain = [('id', 'in', [term15, term30])]
        return domain

    payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms', default=default_payment_term_id, domain=domain_payment_term_id)

    credit_limit = fields.Monetary(currency_field='currency_id', string='Credit Limit')
    credit_limit_sisa = fields.Monetary(currency_field='currency_id', string='Sisa Credit Limit')

    credit_limit_notes = fields.Text(string='Notes')
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        credit_limit = 0
        if self.partner_id:
            credit_limit = self.partner_id.credit_limit
        self.credit_limit = credit_limit

    # @api.onchange('partner_id')
    # def onchange_default_invoice_id(self):
    #     parent_id = self.partner_id.id
    #     model = self.env['res.partner']
    #     inv_add_id = model.search([('parent_id', '=', parent_id),('type', '=', 'invoice')])
    #     if inv_add_id:
    #         for rec in inv_add_id:
    #             self.partner_invoice_id = rec.id
    #     else:
    #         self.partner_invoice_id = parent_id
    #     ship_add_id = model.search([('parent_id', '=', parent_id),('type', '=', 'delivery')])
    #     if ship_add_id:
    #         for rec in ship_add_id:
    #             self.partner_shipping_id = rec.id
    #     else:
    #         self.partner_shipping_id = parent_id

    @api.depends('partner_id')
    @api.onchange('partner_id')
    def onchange_domain_partner(self):
        domain = {}
        model = self.env['res.partner']
        if self.partner_id:
            parent_id = self.partner_id.id
            child_ids = model.search([('parent_id', '=', parent_id)])
            if child_ids:
                domain['partner_invoice_id'] = [('parent_id', '=', parent_id), ('type', '=', 'invoice')]
                domain['partner_shipping_id'] = [('parent_id', '=', parent_id), ('type', '=', 'delivery')]
            else:
                domain['partner_invoice_id'] = [('id', '=', parent_id)]
                domain['partner_shipping_id'] = [('id', '=', parent_id)]
        else:
            self.partner_invoice_id = False
            self.partner_shipping_id = False
        return {'domain': domain}

    partner_invoice_id = fields.Many2one('res.partner', string='Invoice Address', readonly=True, required=True,
                                         states={'draft': [('readonly', False)], 'sent': [('readonly', False)],
                                                 'sale': [('readonly', False)]},
                                         help="Invoice address for current sales order.")
    partner_shipping_id = fields.Many2one('res.partner', string='Delivery Address', readonly=True, required=True,
                                          states={'draft': [('readonly', False)], 'sent': [('readonly', False)],
                                                  'sale': [('readonly', False)]},
                                          help="Delivery address for current sales order.")

    customer_po_number = fields.Char()
    customer_po_date = fields.Date()

    confirmation_date = fields.Datetime(string='Confirmation Date', readonly=False, index=True,
                                        help="Date on which the sale order is confirmed.",
                                        oldname="date_confirm", copy=False)
    is_force_date_sales_order = fields.Boolean(related='company_id.is_force_date_sales_order')

    @api.multi
    def action_confirm(self):
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])

        values = {'state': 'sale'}

        if not self.is_force_date_sales_order:
            values['confirmation_date'] = fields.Datetime.now()

        self.write(values)
        self._action_confirm()
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()
        return True

class SaleLine(models.Model):
    _inherit = "sale.order.line"
    _description = 'Inherit Sale Order Line'

    operating_unit_id = fields.Many2one('operating.unit', related='order_id.operating_unit_id', store=True, string="Unit")
    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)
    tax_id = fields.Many2many('account.tax', string='Tax', domain=['|', ('active', '=', False), ('active', '=', True)])


class SaleReport(models.Model):
    _inherit = "sale.report"
    _description = 'Inherit Sale Order Report'

    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['operating_unit_id'] = ", s.operating_unit_id as operating_unit_id"
        groupby += ', s.operating_unit_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
