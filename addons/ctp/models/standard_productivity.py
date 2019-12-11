# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StandardProductivity(models.Model):
    _name = 'berdikari.standard.productivity'
    _description = 'Berdikari Standard Productivity'

    asset_id = fields.Many2one('product.template')
    vendor_id = fields.Many2one('res.partner')
    by_date = fields.Date()

    std_prod_line_ids = fields.One2many('berdikari.standard.productivity.line', 'std_productivity_id')


class StandardProductivityLine(models.Model):
    _name = 'berdikari.standard.productivity.line'
    _description = 'Berdikari Standard Productivity Line'

    std_productivity_id = fields.Many2one('berdikari.standard.productivity')
    week = fields.Integer()
    pe_he = fields.Integer(string='PE/HE')
    he_hh = fields.Integer(string='HE/HH')
    female_depletion = fields.Integer(string='Female')
    male_depletion = fields.Integer(string='Male')
