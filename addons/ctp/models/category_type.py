# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CategoryType(models.Model):
    _name = 'berdikari.hr.category.type'
    _description = 'Berdikari HR Category Type'

    code = fields.Char()
    name = fields.Char()
    remarks = fields.Text()
    active = fields.Boolean()

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active