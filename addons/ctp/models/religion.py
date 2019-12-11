# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Religion(models.Model):
    _name = 'berdikari.religion'
    _description = 'Berdikari Religion'

    code = fields.Char()
    name = fields.Char()
    is_moslem = fields.Boolean(string='Moslem')
    remarks = fields.Text()
    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active