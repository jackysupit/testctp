# -*- coding: utf-8 -*-

from odoo import models, fields, api


class JobLevel(models.Model):
    _name = 'berdikari.hr.job.level'
    _description = 'Berdikari HR Job Level'

    code = fields.Char()
    name = fields.Char()
    remarks = fields.Text()
    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active