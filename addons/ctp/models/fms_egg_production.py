# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class FMSEggProduction(models.Model):
    _name = 'berdikari.fms.egg.production'
    _rec_name = 'number'

    number = fields.Char(string='Number', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.fms.egg.production'))
    date = fields.Date()
    file_name = fields.Char()
    src_company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    notes = fields.Text()
    fms_egg_production_detail = fields.One2many('berdikari.fms.egg.production.line','fms_egg_production_id',string='FMS Egg Production Detail')

    def compute_fms_egg_production_line2(self):
        for rec in self:
            rec.fms_egg_production_line2 = rec.fms_egg_production_detail
    fms_egg_production_line2 = fields.One2many('berdikari.fms.egg.production.line','fms_egg_production_id', compute='compute_fms_egg_production_line2')

    def compute_fms_egg_production_line3(self):
        for rec in self:
            rec.fms_egg_production_line3 = rec.fms_egg_production_detail
    fms_egg_production_line3 = fields.One2many('berdikari.fms.egg.production.line','fms_egg_production_id', compute='compute_fms_egg_production_line2')

    def compute_fms_egg_production_line4(self):
        for rec in self:
            rec.fms_egg_production_line4 = rec.fms_egg_production_detail
    fms_egg_production_line4 = fields.One2many('berdikari.fms.egg.production.line','fms_egg_production_id', compute='compute_fms_egg_production_line2')

    def compute_fms_egg_production_line5(self):
        for rec in self:
            rec.fms_egg_production_line5 = rec.fms_egg_production_detail
    fms_egg_production_line5 = fields.One2many('berdikari.fms.egg.production.line','fms_egg_production_id', compute='compute_fms_egg_production_line2')

    def compute_fms_egg_production_line6(self):
        for rec in self:
            rec.fms_egg_production_line6 = rec.fms_egg_production_detail
    fms_egg_production_line6 = fields.One2many('berdikari.fms.egg.production.line','fms_egg_production_id', compute='compute_fms_egg_production_line2')

    status = fields.Selection([(1, 'Open'),(2, 'Draft'), (3, 'Approved')], default=1)



    # @api.model
    # def create(self, vals):
    #     rec = super(FMSEggProduction, self).create(vals)
    #     for one in rec.fms_egg_production_detail:
    #         one.is_open = True
    #     return rec
    #
    #
    # @api.multi
    # def write(self, vals):
    #     return_dari_parent = super(FMSEggProduction, self).write(vals)
    #     # return_dari_parent == True // kecuali error
    #     for rec in self:
    #         for one in rec.fms_egg_production_detail:
    #             one.is_open = True
    #     return True

    #buat vinny,
    # kalo udah selesai, delete this comment
    #1. tambahin _rec_name = 'number'
    #2. set default number = sequences for fms.egg.production
    #3. set default company = current company


class FMSEggProductionDetail(models.Model):
    _name = 'berdikari.fms.egg.production.line'
    _description = 'Berdikari Egg Production Line'

    fms_egg_production_id = fields.Many2one('berdikari.fms.egg.production')
    status = fields.Selection([(1, 'Open'),(2, 'Draft'), (3, 'Approved')], related='fms_egg_production_id.status', store=True)

    finished_goods = fields.Many2one('mrp.production')
    flock = fields.Many2one('berdikari.flock.master')
    chicken_coop = fields.Many2one('berdikari.chicken.coop')
    date = fields.Date()
    weeks = fields.Integer()
    age = fields.Integer(string='Age(Days)')
    death = fields.Boolean()
    by_product = fields.Char()
    on_hand = fields.Boolean()
    egg_in = fields.Boolean()
    egg_in_by_product = fields.Boolean()
    feed_name = fields.Many2one('product.template')
    feed_code = fields.Char(related='feed_name.default_code')
    standard = fields.Char()
    actual = fields.Char()
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure')
    temperature = fields.Float()
    humidity = fields.Float()
    light = fields.Float()
    medicine_name = fields.Many2one('product.template')
    medicine_code = fields.Char(related='medicine_name.default_code')
    medicine_qty = fields.Float()
    medicine_uom_id = fields.Many2one('uom.uom', 'Medicine UOM')
    vaccine_name = fields.Many2one('product.template')
    vaccine_code = fields.Char(related='vaccine_name.default_code')
    vaccine_qty = fields.Float()
    vaccine_uom_id = fields.Many2one('uom.uom', 'Vaccine UOM')
    chemical_name = fields.Many2one('product.template')
    chemical_code = fields.Char(related='chemical_name.default_code')
    chemical_qty = fields.Float()
    chemical_uom_id = fields.Many2one('uom.uom', 'Chemical UOM')
    weight = fields.Float()
    weight_uom_id = fields.Many2one('uom.uom', 'Weight UOM')
    remark = fields.Text()
    # material use tab
    manufacturing_order_id = fields.Char()
    # death tab
    biological_assets_name = fields.Many2one('product.template')
    biological_assets_code = fields.Char(related='biological_assets_name.default_code')
    biological_assets_qty = fields.Float()
    biological_assets_uom_id = fields.Many2one('uom.uom', 'Biological UOM')
    # egg in tab
    egg_in_name = fields.Many2one('product.template')
    egg_in_code = fields.Char(related='egg_in_name.default_code')
    egg_in_qty = fields.Float()
    egg_in_uom_id = fields.Many2one('uom.uom', 'Egg In UOM')
    # egg in by product tab
    egg_in_by_product_name = fields.Many2one('product.template')
    egg_in_by_product_code = fields.Char(related='egg_in_by_product_name.default_code')
    egg_in_by_product_qty = fields.Float()
    egg_in_by_product_uom_id = fields.Many2one('uom.uom', 'Egg In By Product UOM')

    is_open = fields.Boolean()
