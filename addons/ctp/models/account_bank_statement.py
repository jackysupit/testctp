# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    is_audit_period = fields.Boolean('Audit Period')
    operating_unit_id = fields.Many2one('operating.unit', string='Unit', default=lambda self: self.env.user.default_operating_unit_id)

    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)

