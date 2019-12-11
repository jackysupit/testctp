# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo.addons.jekdoo.utils.util import Util
import datetime

class Invoice(models.Model):
    _inherit = "account.invoice"

    credit_limit = fields.Monetary(currency_field='currency_id', string='Credit Limit')
    credit_limit_sisa = fields.Monetary(currency_field='currency_id', string='Sisa Credit Limit')

    credit_limit_notes = fields.Text(string='Notes')
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        credit_limit = 0
        if self.partner_id:
            credit_limit = self.partner_id.credit_limit
        self.credit_limit = credit_limit

    @api.onchange('origin')
    @api.depends('origin')
    def get_schedule_date(self):
        po = self.origin
        if po:
            modelPurchase = self.env['purchase.order']
            po_id = modelPurchase.search([('name', '=', po)], limit=1)
            order_date = po_id.date_order
            self.order_date_po = order_date.date()
            for rec in po_id.order_line:
                schedule = rec.date_planned
                self.schedule_date = schedule.date()
    schedule_date = fields.Date()
    order_date_po = fields.Date(string='Order Date')

    class InvoiceLine(models.Model):
        _inherit = "account.invoice.line"

        is_ppn_gt_one_million = fields.Boolean(related='invoice_id.is_ppn_gt_one_million')