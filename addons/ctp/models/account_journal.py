# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)
    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)

    @api.multi
    def name_get(self):
        res = []
        for journal in self:
            company = journal.company_id
            currency = journal.currency_id or journal.company_id.currency_id
            name = "%s (%s, %s)" % (journal.name, currency.name, company.name)
            res += [(journal.id, name)]
        return res

