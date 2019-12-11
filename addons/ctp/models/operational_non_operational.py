# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HoseMaster(models.Model):
    _name = 'berdikari.operational.non.operational'
    _description = 'Berdikari Operational Non Operational'

    code = fields.Char()
    name = fields.Char(required=True)
    type = fields.Selection(selection=([('operational', 'Operational'), ('non operational', 'Non Operational')]))
    remarks = fields.Text()
    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active
