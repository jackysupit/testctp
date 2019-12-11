# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.jekdoo.utils.util import Util
import logging
_logger = logging.getLogger(__name__)


class PaymentRequest(models.Model):
    _name = 'berdikari.payment.request'
    _description = 'Berdikari Payment Request'

    name = fields.Char(string='Payment Request number', domain=[('invisible','=',True)])
    employee_id = fields.Many2one('hr.employee',string='Responsble', default=lambda self: self.env.user.employee_id.id)
    # employee_id = fields.Many2one('hr.employee',string='Responsble')
    job_id = fields.Many2one('hr.job',string='Position', related='employee_id.job_id')
    currency_id = fields.Many2one('res.currency', string='Currency', store=True)

    requested_date = fields.Date(string='Date')
    # amount_total_payment = fields.Monetary(currency_field='currency_id', store=True, string='Total Request Payment')
    amount_total_payment = fields.Float(compute = '_compute_total_payment', string='Total Request Payment')
    payment_req = fields.One2many('berdikari.payment.request.line','payment_req_id')
    payment_req_line = fields.One2many('berdikari.payment.request.line','payment_req_id')
    status = fields.Boolean(default = False)

    @api.model_create_multi
    def create(self, vals_list):
        IrSequence = self.env['ir.sequence']
        name = IrSequence.next_by_code('berdikari.payment.request')
        vals_list[0]['name'] = name
        vals_list[0]['status'] = True
        rec = super(PaymentRequest, self).create(vals_list)
        return rec

    @api.multi
    def _compute_total_payment(self):
        for rec in self:
            rec.amount_total_payment = sum(line.amount_total_signed for line in rec.payment_req)

class PaymentRequestLine(models.Model):
    _name = 'berdikari.payment.request.line'
    _description = 'Berdikari payment Request line'

    selected_bill_ids = [] #id yang sudah dipilih

    payment_req_id = fields.Many2one('berdikari.payment.request')
    status = fields.Boolean(related='payment_req_id.status', store=True)

    @api.onchange('bill_id')
    def domain_bill_id(self):
        if self.bill_id:
            self.selected_bill_ids.append(self.bill_id.id)

        domain = {}
        domain['bill_id'] = [('number', 'like', 'BILL/')]

        if self.selected_bill_ids:
            domain['bill_id'].append(('id', 'not in', self.selected_bill_ids))
        return {
            'domain': domain
        }

    bill_id = fields.Many2one('account.invoice',string='Nomor Invoice')

    bill_id_currency_id = fields.Many2one('res.currency', string='Currency', related='bill_id.currency_id', store=True)
    vendor_name = fields.Char(related='bill_id.vendor_display_name',string='Vendor')
    company = fields.Many2one(related='bill_id.company_id')
    bill_date = fields.Date(related='bill_id.date_invoice')
    due_date = fields.Date(related='bill_id.date_due')
    source_doc = fields.Char(related='bill_id.origin', string='Source Document')
    amount_untaxed = fields.Monetary(related='bill_id.amount_untaxed', currency_field='bill_id_currency_id', string='Tax Excloude', store=True)
    amount_tax = fields.Monetary(related='bill_id.amount_tax', currency_field='bill_id_currency_id', string='Tax', store=True)
    amount_total_signed = fields.Monetary(related='bill_id.amount_total_signed', currency_field='bill_id_currency_id', string='Total', store=True)

    is_approve = fields.Boolean(string='Approved')



