# -*- coding: utf-8 -*-

from odoo import models, fields, api

class GenerateAssetsEntriesWizard(models.TransientModel):
    _inherit = 'asset.depreciation.confirmation.wizard'
    _description = 'inherit Asset Depreciation Confirmation Wizard'

    company = fields.Many2one('res.company', string='Company', required=True)