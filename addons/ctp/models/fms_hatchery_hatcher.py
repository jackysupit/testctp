# # -*- coding: utf-8 -*-
# from odoo.exceptions import ValidationError
# from odoo import models, fields, api, _
# from datetime import timedelta, datetime
# from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
# import logging
# _logger = logging.getLogger(__name__)
#
#
# class FMSHatcheryHatcher(models.Model):
#     _name = 'berdikari.fms.hatchery.hatcher'
#     _description = 'FMS Hatchery Hatcher'
#
#     fms_hatchery_id = fields.Many2one('berdikari.fms.hatchery')
#     name = fields.Char(string='Hatcher ID', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.fms.hatchery.hatcher'))
#     def default_date_hacher(self):
#         ctx = self._context
#         date = ctx.get('adefault_date')
#         date = datetime.strptime(date, DEFAULT_SERVER_DATE_FORMAT)
#         new_date = date + timedelta(days=18)
#         return  new_date.date()
#
#
#     date = fields.Date(default=default_date_hacher)
#     farm = fields.Char(string='Farm/ Unit')
#     hatcher_machine_id = fields.Many2one('berdikari.farm.machine', domain=[('type', '=', 'hatcher')], string=" Unit")
#     capacity = fields.Integer(related='hatcher_machine_id.capacity')
#     he_received = fields.Integer()
#     he_infertile = fields.Integer()
#     he_explode = fields.Integer()
#     he_fertile = fields.Integer()
#     dis = fields.Integer()
#     cuddling_doc = fields.Integer()
#     salable_chick = fields.Integer()
#
#     state = fields.Selection([('draft', '-'),('done', 'Done'),], default='draft')
#     def compute_is_done(self):
#         for rec in self:
#             rec.is_done = rec.state == 'done'
#     is_done = fields.Boolean(string='Done', compute=compute_is_done)
#
#     flock = fields.Many2one('berdikari.master.flock')
#
#     @api.onchange('he_received', 'he_infertile', 'he_explode', 'dis', 'cuddling_doc')
#     def onchange_hitung_fertile(self):
#         for rec in self:
#             rec.he_fertile = rec.he_received - rec.he_infertile - rec.he_explode
#             rec.salable_chick = rec.he_fertile - rec.dis - rec.cuddling_doc
#
#     @api.onchange('total_he_received')
#     def onchange_hitung_fertile(self):
#         for rec in self:
#             if rec.capacity < rec.he_received:
#                 raise ValidationError(_('Over capacity'))
#
#
# class FMSHatcheryHatcherReceived(models.Model):
#     _name = 'berdikari.fms.hatchery.hatcher.received'
#     _description = 'FMS Hatchery Hacther Received'
#
#     fms_hatchery_id = fields.Many2one('berdikari.fms.hatchery')
#     name = fields.Char(string='Hatcher ID', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.fms.hatchery.hatcher'))
#     date = fields.Date()
#     setter_id = fields.Many2one('berdikari.fms.hatchery.setter')
#     farm = fields.Char(string='Farm/ Unit')
#     he_received = fields.Integer()
#     he_infertile = fields.Integer()
#     he_explode = fields.Integer()
#     he_fertile = fields.Integer()
#     flock = fields.Many2one('berdikari.master.flock')
#
#
# class FMSHatcheryHatcherResult(models.Model):
#     _name = 'berdikari.fms.hatchery.hatcher.result'
#     _description = 'FMS Hatchery Hacther Result'
#
#     fms_hatchery_id = fields.Many2one('berdikari.fms.hatchery')
#     name = fields.Char(string='Hatcher ID', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.fms.hatchery.hatcher'))
#     date = fields.Date()
#     farm = fields.Char(string='Farm/ Unit')
#     fertile = fields.Integer()
#     dis = fields.Integer()
#     cuddling_doc = fields.Integer()
#     salable_chick = fields.Integer()
#     sex = fields.Selection(selection=[
#         ('male', 'Male'),
#         ('female', 'Female'),
#     ])
#     qty = fields.Integer()
#     uom_id = fields.Many2one('uom.uom')
#     flock = fields.Many2one('berdikari.master.flock')
#
#
# class FMSHatcheryHatcherSalableChick(models.Model):
#     _name = 'berdikari.fms.hatchery.hatcher.salable.chick'
#     _description = 'FMS Hatchery Hacther Salable Chick'
#
#     fms_hatchery_id = fields.Many2one('berdikari.fms.hatchery')
#     salable_item = fields.Char()
#     sex = fields.Selection(selection=[
#         ('male', 'Male'),
#         ('female', 'Female'),
#     ])
#     qty = fields.Integer()
#     uom_id = fields.Many2one('uom.uom')
#
#
#
