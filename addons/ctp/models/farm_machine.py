# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FarmMachine(models.Model):
    _name = 'berdikari.farm.machine'
    _description = 'Berdikari Farm Machine'

    code = fields.Char(string='Code',required=True)
    name = fields.Char(required=True)
    capacity = fields.Integer(required=True)
    type = fields.Selection(selection=[('setter', 'Setter'), ('hatcher', 'Hatcher')])
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)

    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)


    notes = fields.Text()
    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active