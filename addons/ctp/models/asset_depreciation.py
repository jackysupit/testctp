# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AssetDepreciation(models.Model):
    _name = 'berdikari.asset.depreciation'
    _description = 'Berdikari Asset Depreciation'

    asset_category = fields.Char()
    reference = fields.Char()
    date = fields.Date()
    depreciation_date = fields.Date()
    first_depreciation_date = fields.Date()
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    currency_id = fields.Many2one('res.currency', string='Currency', store=True)
    src_company_id = fields.Many2one('res.company', string='Company', required=True,
                                     default=lambda self: self.env.user.company_id)
    gross_value = fields.Float()
    salvage_value =  fields.Float()
    residual_value = fields.Float()
    asset_value = fields.Float()
    vendor_id = fields.Many2one('res.partner', domain=[('supplier','=',True),('is_company','=',True)])
    invoice = fields.Char()

    computation_method = fields.Selection(selection=([('none', 'None'), ('slm', 'SLM'), ('ddm', 'DDM')]))
    degresive_factor = fields.Float()
    time_method_base = fields.Char(string='Time Metod Base On')
    prorate_temporis = fields.Float()
    numbers_of_depreciations = fields.Float()
    number_of_month_in_period = fields.Integer(string='Number Of Month in a period')
    is_next_month_depreciation = fields.Boolean(string='15th above will be next month depreciation')
    is_can_reclass = fields.Boolean(string='Can be Reclass')

    asset_depreciation_detail = fields.One2many('berdikari.asset.depreciation.line', 'asset_depreciation_id')

    def _compute_asset_depreciation_line2(self):
        for rec in self:
            rec.asset_depreciation_line2 = rec.asset_depreciation_detail
    asset_depreciation_line2 = fields.One2many('berdikari.asset.depreciation.line', 'asset_depreciation_id', compute='_compute_asset_depreciation_line2')


class AssetDepreciationLine(models.Model):
    _name = 'berdikari.asset.depreciation.line'

    asset_depreciation_id = fields.Many2one('berdikari.asset.depreciation')
    line_depreciation_date = fields.Date()
    depreciation = fields.Float()
    cummulative_depreciation = fields.Float()
    residual = fields.Char()
