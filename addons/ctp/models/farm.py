# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Farm(models.Model):
    _inherit = 'operating.unit'
    _description = 'Berdikari Farm'

    code = fields.Char()
    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    stock_location_id = fields.Many2one('stock.location', string='Stock Location', required=True)
    remarks = fields.Text()
    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active