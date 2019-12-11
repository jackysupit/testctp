# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HoseMaster(models.Model):
    _name = 'berdikari.document.type'
    _description = 'Berdikari Document Type'

    code = fields.Char()
    name = fields.Char(required=True)
    days_before_expired_warning = fields.Integer()
    remarks = fields.Text()
    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active
