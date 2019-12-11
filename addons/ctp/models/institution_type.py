# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HoseMaster(models.Model):
    _name = 'berdikari.institution.type'
    _description = 'Berdikari Institution Type'

    code = fields.Char()
    name = fields.Char(required=True)
    remarks = fields.Text()
    active = fields.Boolean()

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active
