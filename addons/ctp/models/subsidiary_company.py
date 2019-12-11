# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class SubsidiaryCompany(models.Model):
    _name = 'berdikari.subsidiary.company'
    _description = 'Berdikari Subsidiary Company'

    name = fields.Char(string='Number')
    date = fields.Date()
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    type = fields.Selection(selection=[('realization', 'Realization'), ('budget', 'Budget')])
    subs_company = fields.Char(string='Subs. Company')

    def default_year(self):
        ret = datetime.datetime.now().strftime('%Y')
        return ret
    period_year = fields.Integer(default=default_year)

    def default_month(self):
        ret = datetime.datetime.now().strftime('%m')
        return ret
    period_month = fields.Integer(default=default_month)
    file_name = fields.Char()
    notes = fields.Text()

    subs_company_line_ids = fields.One2many('berdikari.subsidiary.company.line', 'sub_company_id')


class SubsidiaryCompanyLine(models.Model):
    _name = 'berdikari.subsidiary.company.line'
    _description = 'Berdikari Subsidiary Company Line'

    sub_company_id = fields.Many2one('berdikari.subsidiary.company')
    line = fields.Char()
    account_code = fields.Char()
    account_name = fields.Char()
    erp_account_code = fields.Char(string='ERP Account Code')
    erp_account_name = fields.Char(string='ERP Account Name')
    begin = fields.Integer()
    currency_id = fields.Many2one('res.currency', string='Currency', store=True)
    debit = fields.Monetary(currency_field='currency_id', store=True)
    credit = fields.Monetary(currency_field='currency_id', store=True)
    end = fields.Integer()