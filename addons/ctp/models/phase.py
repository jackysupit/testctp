# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Phase(models.Model):
    _name = 'berdikari.phase'
    _description = 'Berdikari Phase Master'

    code = fields.Char(string='Code',required=True)
    name = fields.Char(required=True)
    duration = fields.Integer(string='Duration Standard (Weeks)')
    material_type = fields.Selection(selection=[
        (1, 'Adding Value (for asset)'),
        (2, 'Inventory Transfer'),
    ])
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    farm_id = fields.Many2one('operating.unit', string=" Unit")

    active = fields.Boolean(string='Not Active', default=True)
    notes = fields.Text()