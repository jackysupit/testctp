# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HoseMaster(models.Model):
    _name = 'berdikari.chicken.coop'
    _description = 'Berdikari Hose Master'

    code = fields.Char(string='Code', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.chicken.coop'))
    name = fields.Char(required=True)
    biological_assets = fields.Many2one('product.template')
    src_company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    notes = fields.Text()
    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)

    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)


    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active
