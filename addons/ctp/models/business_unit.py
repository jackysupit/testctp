# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HoseMaster(models.Model):
    _name = 'berdikari.business.unit'
    _description = 'Berdikari Business Unit'

    code = fields.Char()
    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    remarks = fields.Text()
    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active
