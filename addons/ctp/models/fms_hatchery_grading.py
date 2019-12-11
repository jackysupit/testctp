# # -*- coding: utf-8 -*-
#
# from odoo import models, fields, api
# import logging
# _logger = logging.getLogger(__name__)
#
#
# class HeBatch(models.Model):
#     _name = 'berdikari.wo.batch'
#     _description = 'HE Batch'
#
#     name = fields.Char(string='Name')
#
#
# class FMSHatcheryGrading(models.Model):
#     _name = 'berdikari.fms.hatchery.grading'
#     _description = 'FMS Hatchery Grading'
#
#     fms_hatchery_id = fields.Many2one('berdikari.fms.hatchery')
#
#
#     name = fields.Char(string='Grading ID', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.fms.hatchery.grading'))
#     date = fields.Date()
#     farm_unit_id = fields.Many2one('berdikari.farm.machine', string=" Unit")
#     house_id = fields.Many2one('berdikari.chicken.coop', string='House')
#     he_receive_qty = fields.Integer(string='HE Received QTY')
#     he_culling_qty = fields.Integer(string='HE Culling QTY')
#     he_qty = fields.Integer(string='HE QTY')
#     flock_id = fields.Many2one('berdikari.flock.master', string='Flock')
#     he_batch_id = fields.Many2one('berdikari.wo.batch', string='HE Batch')
#
#
# class FMSHatcheryGradingDeath(models.Model):
#     _name = 'berdikari.fms.hatchery.grading.death'
#     _description = 'FMS Hatchery Grading / Deatch'
#
#     fms_hatchery_id = fields.Many2one('berdikari.fms.hatchery')
#     product_template_id = fields.Many2one('product.template', string='Assets Name')
#     product_template_code = fields.Char(related='product_template_id.default_code', string='Assets ID')
#     product_template_type = fields.Selection([
#                         ('consu', 'Consumable'),
#                         ('service', 'Service'),
#                         ('product', 'Storable Product'),
#     ], string='Product Type', related='product_template_id.type',)
#     sex = fields.Selection(selection=[
#         ('male', 'Male'),
#         ('female', 'Female'),
#     ])
#     begin_qty = fields.Integer(string='Begin QTY')
#     death_qty = fields.Integer(string='Death QTY')
#     ending_qty = fields.Integer(string='Ending QTY')
#
#
# class FMSHatcheryGradingFeed(models.Model):
#     _name = 'berdikari.fms.hatchery.grading.feed'
#     _description = 'FMS Hatchery Grading / Feed'
#
#     fms_hatchery_id = fields.Many2one('berdikari.fms.hatchery')
#     product_template_id = fields.Many2one('product.template', string='Material Name')
#     product_template_code = fields.Char(related='product_template_id.default_code', string='Material Code')
#     uom_id = fields.Many2one('uom.uom', string='UOM')
#     he_batch_id = fields.Many2one('berdikari.wo.batch', string='HE Batch')
#
#     qty = fields.Integer(string='QTY')
#     sex = fields.Selection(selection=[
#         ('male', 'Male'),
#         ('female', 'Female'),
#     ])
#
#
# class FMSHatcheryGradingByProduct(models.Model):
#     _name = 'berdikari.fms.hatchery.grading.byproduct'
#     _description = 'FMS Hatchery Grading / By Product'
#
#     fms_hatchery_id = fields.Many2one('berdikari.fms.hatchery')
#     product_template_id = fields.Many2one('product.template', string='Material Name')
#     product_template_code = fields.Char(related='product_template_id.default_code', string='Material Code')
#     uom_id = fields.Many2one('uom.uom', string='UOM')
#     qty = fields.Integer(string='QTY')
#
#
# class FMSHatcheryGradingOVK(models.Model):
#     _name = 'berdikari.fms.hatchery.grading.ovk'
#     _description = 'FMS Hatchery Grading / Other Material (OVK)'
#
#     fms_hatchery_id = fields.Many2one('berdikari.fms.hatchery')
#     product_template_id = fields.Many2one('product.template', string='Material Name')
#     product_template_code = fields.Char(related='product_template_id.default_code', string='Material Code')
#     he_batch_id = fields.Many2one('berdikari.wo.batch', string='HE Batch')
#
#     uom_id = fields.Many2one('uom.uom', string='UOM')
#     qty = fields.Integer(string='QTY')