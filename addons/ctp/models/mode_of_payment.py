# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ModeOfPayment(models.Model):
    _name = 'berdikari.mode.of.payment'
    _description = 'Berdikari Mode Of Payment'

    code = fields.Char()
    name = fields.Char(required=True)
    is_credit = fields.Boolean(string='Credited')
    remarks = fields.Text()
    journal_type = fields.Selection(selection=[('bank', 'Bank'), ('cash', 'Cash')])
    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active
