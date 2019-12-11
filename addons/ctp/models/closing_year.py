# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class ClosingYear(models.Model):
    _name = 'berdikari.closing.year'
    _description = 'Berdikari Closing Year'

    name = fields.Char(string='Number')
    date = fields.Date()
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    journal_id = fields.Many2one('account.account.type')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')

    def default_year(self):
        ret = datetime.datetime.now().strftime('%Y')
        return ret
    period_year = fields.Integer(default=default_year)

    def default_month(self):
        ret = datetime.datetime.now().strftime('%m')
        return ret
    period_month = fields.Integer(default=default_month)
    notes = fields.Text()

    closing_year_line_ids = fields.One2many('berdikari.closing.year.line', 'closing_year_id')


class ClosingYearLine(models.Model):
    _name = 'berdikari.closing.year.line'
    _description = 'Berdikari Closing Year Line'

    closing_year_id = fields.Many2one('berdikari.closing.year')
    account_code = fields.Char()
    account_name = fields.Char()
    currency_id = fields.Many2one('res.currency', string='Currency', store=True)
    debit = fields.Monetary(currency_field='currency_id', store=True)
    credit = fields.Monetary(currency_field='currency_id', store=True)


