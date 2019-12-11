# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EducationLevel(models.Model):
    _name = 'berdikari.hr.education.level'
    _description = 'Berdikari Education Level'

    code = fields.Char()
    name = fields.Char()
    remarks = fields.Text()
    certification_level = fields.Char()
    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active