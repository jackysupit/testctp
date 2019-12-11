# # -*- coding: utf-8 -*-
# from odoo.exceptions import ValidationError
# from odoo import models, fields, api, _
# import logging
# _logger = logging.getLogger(__name__)
#
#
# class FMSHatcherySetter(models.Model):
#     _name = 'berdikari.fms.hatchery.setter'
#     _description = 'FMS Hatchery Setter'
#
#     # fms_hatchery_id = fields.Many2one('berdikari.fms.hatchery')
#     parent_id = fields.Many2one('berdikari.fms.grading.setter')
#
#
#     name = fields.Char(string='Setter ID', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.fms.hatchery.setter'))
#     date = fields.Date()
#     farm = fields.Char(string='Farm/ Unit')
#     setter_machine_id = fields.Many2one('berdikari.farm.machine', domain=[('type', '=', 'setter')], string=" Unit")
#     capacity = fields.Integer(related='setter_machine_id.capacity')
#     total_he_received = fields.Integer()
#     total_he_culling = fields.Integer()
#     total_he = fields.Integer()
#     infertile = fields.Integer()
#     explode = fields.Integer()
#     fertile = fields.Integer()
#     flock = fields.Many2one('berdikari.master.flock')
#
#     state = fields.Selection([('draft', '-'),('done', 'Done'),], default='draft')
#     def compute_is_done(self):
#         for rec in self:
#             rec.is_done = rec.state == 'done'
#     is_done = fields.Boolean(string='Done', compute=compute_is_done)
#
#     @api.onchange('total_he_received', 'total_he_culling', 'infertile', 'explode')
#     def onchange_hitung_fertile(self):
#         for rec in self:
#             rec.total_he = rec.total_he_received - rec.total_he_culling
#             rec.fertile = rec.total_he -rec.infertile - rec.explode
#
#     @api.onchange('total_he_received')
#     def onchange_hitung_fertile(self):
#         for rec in self:
#             if rec.capacity < rec.total_he_received:
#                 raise ValidationError(_('Over capacity'))
#
#
# class FMSHatcherySetterReceived(models.Model):
#     _name = 'berdikari.fms.hatchery.setter.received'
#     _description = 'FMS Hatchery Setter Received'
#
#     # fms_hatchery_id = fields.Many2one('berdikari.fms.hatchery', string='Hatchery ID')
#     parent_id = fields.Many2one('berdikari.fms.grading.setter')
#
#     name = fields.Char(string='Setter ID', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.fms.hatchery.setter'))
#     date = fields.Date()
#     grading_id = fields.Many2one('berdikari.fms.hatchery.grading')
#     farm = fields.Char(string='Farm/ Unit')
#     he_received = fields.Integer()
#     he_culling = fields.Integer()
#     he = fields.Integer()
#     flock = fields.Many2one('berdikari.master.flock')
#     he_batch_id = fields.Many2one('berdikari.wo.batch') #ngambil dari master batch
#
#
# class FMSHatcherySetterResult(models.Model):
#     _name = 'berdikari.fms.hatchery.setter.result'
#
#     # fms_hatchery_id = fields.Many2one('berdikari.fms.hatchery', string='Hatchery ID')
#     parent_id = fields.Many2one('berdikari.fms.grading.setter')
#
#     name = fields.Char(string='Setter ID', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.fms.hatchery.setter'))
#     date = fields.Date()
#     farm = fields.Char(string='Farm/ Unit')
#     infertile = fields.Integer()
#     explode = fields.Integer()
#     fertile = fields.Integer()
#     flock = fields.Many2one('berdikari.master.flock')
#
#
#
#
