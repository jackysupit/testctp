# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime


class COGSCosting(models.Model):
    _name = 'berdikari.cogs.costing'
    _description = 'Berdikari COGS Costing'

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

    cogs_reverse_ids = fields.One2many('berdikari.cogs.costing.reverse', 'cogs_costing_id')
    cogs_correction_ids = fields.One2many('berdikari.cogs.costing.correction', 'cogs_costing_id')
    cogs_journal_ids = fields.One2many('berdikari.cogs.costing.journal', 'cogs_costing_id')


class COGSCostingReverse(models.Model):
    _name = 'berdikari.cogs.costing.reverse'
    _description = 'Berdikari COGS Costing Reverse'

    cogs_costing_id = fields.Many2one('berdikari.cogs.costing')
    account_code = fields.Char()
    account_name = fields.Char()
    currency_id = fields.Many2one('res.currency', string='Currency', store=True)
    debit = fields.Monetary(currency_field='currency_id', store=True)
    credit = fields.Monetary(currency_field='currency_id', store=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)

    flock_id = fields.Many2one('berdikari.flock.master')


class COGSCostingCorrection(models.Model):
    _name = 'berdikari.cogs.costing.correction'
    _description = 'Berdikari COGS Costing Correction'

    cogs_costing_id = fields.Many2one('berdikari.cogs.costing')
    account_code = fields.Char()
    account_name = fields.Char()
    currency_id = fields.Many2one('res.currency', string='Currency', store=True)
    debit = fields.Monetary(currency_field='currency_id', store=True)
    credit = fields.Monetary(currency_field='currency_id', store=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)

    flock_id = fields.Many2one('berdikari.flock.master')


class COGSCostingJournal(models.Model):
    _name = 'berdikari.cogs.costing.journal'
    _description = 'Berdikari COGS Costing Journal'

    cogs_costing_id = fields.Many2one('berdikari.cogs.costing')
    account_code = fields.Char()
    account_name = fields.Char()
    currency_id = fields.Many2one('res.currency', string='Currency', store=True)
    debit = fields.Monetary(currency_field='currency_id', store=True)
    credit = fields.Monetary(currency_field='currency_id', store=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)

    flock_id = fields.Many2one('berdikari.flock.master')