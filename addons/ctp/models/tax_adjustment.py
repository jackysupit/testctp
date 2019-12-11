# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TaxAdjustmentWizard(models.TransientModel):
    _inherit = 'tax.adjustments.wizard'
    _description = 'Inherit Tax Adjustment Wizard'

    notes = fields.Text(string='Notes')
    is_credited = fields.Boolean(string='Can be Credited')
    vat_number = fields.Char(string='VAT Number')
    vat_date = fields.Date(string='VAT Date')
    partner_id = fields.Many2one('res.partner', string='Partner')
    vat = fields.Char(related='partner_id.vat', string='NPWP')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    partner = fields.Many2one('res.partner')