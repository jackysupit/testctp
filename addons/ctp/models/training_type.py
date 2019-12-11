# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TrainingType(models.Model):
    _name = 'berdikari.hr.training.type'
    _description = 'Berdikari HR Training Type'

    code = fields.Char()
    name = fields.Char()
    remarks = fields.Text()
    active = fields.Boolean()

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active