# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.jekdoo.utils.util import Util


class ReceiveMoneyWizard(models.Model):
    _name = 'receive.money.wizard'
    _description = 'Model for print receive money report'

    name = fields.Char()
    date_from = fields.Date()
    date_to = fields.Date()
    journal_type = fields.Selection([
            ('cash', 'Cash'),
            ('bank', 'Bank'),('all', 'All')
        ],default='all'
    )
    payment_type = fields.Selection([('inbound', 'IN'), ('outbound', 'OUT'), ('transfer', 'Transfer'), ('all', 'All')], default='all')

    @api.depends('date_from', 'date_to')
    @api.onchange('date_from', 'date_to')
    def onchange_date(self):
        for rec in self:
            model_payment = rec.env['account.payment']
            if rec.date_from and rec.date_to:
                rec.name = '{} - {}'.format(rec.date_from, rec.date_to)

                invoice_payment_ids = model_payment.search([('payment_type', '=', 'inbound'),
                    ('payment_date', '>=', rec.date_from), ('payment_date', '<=', rec.date_to)])
            else:
                invoice_payment_ids = model_payment.search([('payment_type', '=', 'inbound')])
            rec.invoice_payment_ids = invoice_payment_ids

    @api.multi
    def action_report_receive_money(self):
        if self.journal_type == False:
            self.journal_type = 'all'
        ctx = {
            'date_range': "{} - {}".format(self.date_from.strftime('%d %m %Y'),
                                           self.date_to.strftime('%d %m %Y'), ),
            'date_from': self.date_from,
            'date_to': self.date_to,
            'search_default_groupby_journal_type': self.journal_type,
        }

        domain = []
        if self.date_from:
            domain.append(('payment_date', '>=', self.date_from))
        else:
            domain = domain
        if self.date_to:
            domain.append(('payment_date', '<=', self.date_to))
        else:
            domain = domain
        if self.journal_type != 'all' and self.journal_type != False:
            domain.append(('journal_type', '=', self.journal_type))
        else:
            domain = domain
        if self.payment_type != 'all' and self.payment_type != False:
            domain.append(('payment_type', '=', self.payment_type))
        else:
            domain = domain

        model_name = 'account.payment'
        action = Util.jek_redirect_to_model(
            title='Receive Money', model_name=model_name, ctx=ctx,
            domain=domain
        )
        return action
