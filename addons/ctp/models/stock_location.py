# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockLocation(models.Model):
    _inherit = 'stock.location'
    _description = 'Inherit Stock Location'

    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)

    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)

