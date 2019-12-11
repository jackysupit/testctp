# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PunishmentType(models.Model):
    _name = 'berdikari.hr.punishment.type'
    _description = 'Berdikari HR Punishment Type'

    code = fields.Char()
    name = fields.Char()
    remarks = fields.Text()
    active = fields.Boolean()

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active