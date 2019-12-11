# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ChartOfAccount(models.Model):
    _inherit = 'account.account'
    _description = 'Inherit Account Account'

    is_tax_pph_account = fields.Boolean(string='Tax (PPh) Account')
    is_pph_credited = fields.Boolean(string='Tax (PPh) Can Be Credited')
    is_tax_ppn_account = fields.Selection(selection=([('moving assets','Moving Asstes'),('non moving assets','Non Moving Assets')]),
                                          string='VAT (PPN) Account')
    is_budget_need_to_check = fields.Boolean(string='Cek for Budget')
    cost_type = fields.Selection(selection=([('direct','Direct'),('indirect','Indirect'),('general admin','General Admin'),('sales','Sales')]))
    is_flock_mandatory = fields.Boolean(string='Flock Mandatory')
    profit_type = fields.Selection(selection=([('all','All'),('manufactures','Manufactures'),('trading','Trading'),('services','Services')]))
    is_cash_advance = fields.Boolean(string='Cash Advance')
    is_down_payment = fields.Boolean(string='Down Payment')
    is_sales_down_payment = fields.Boolean(string='Sales down Payment')


class AssetCateg(models.Model):
    _inherit = 'account.asset.category'
    _description = 'Category Asset Asset'

    sex = fields.Selection([('Male','male'),('Female','female')])


class JournalEntry(models.Model):
    _inherit = 'account.move'
    _description = 'Inherit Account Move'

    audit_period = fields.Boolean(string='Audit Period')


class JournalEntryLine(models.Model):
    _inherit = 'account.move.line'
    _description = 'Inherit Account Move Line'

    flock_id = fields.Many2one('berdikari.flock.master')