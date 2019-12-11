# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FamilyRelation(models.Model):
    _name = 'berdikari.hr.family.relation'
    _description = 'Berdikari Employee Family Relation'

    code = fields.Char()
    name = fields.Char()
    type = fields.Selection([('husband/wife/parents','Husband/Wife/Parents'),('child','Child')])
    remarks = fields.Text()
    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active
