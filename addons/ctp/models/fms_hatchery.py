# # -*- coding: utf-8 -*-
#
# from odoo import models, fields, api, _
# from odoo.exceptions import ValidationError
# import logging
# from datetime import date, datetime, time
# _logger = logging.getLogger(__name__)
#
#
# class FMSHatchery(models.Model):
#     _name = 'berdikari.fms.hatchery'
#     _description = 'FMS Hatchery'
#
#     name = fields.Char(string='Number', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.fms.hatchery'))
#     date = fields.Date(default=lambda self: fields.Date.to_string(date.today()))
#     company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
#
#     work_order_id = fields.Many2one('berdikari.work.order', string='Work Order ID')
#
#     is_validate_setter = fields.Boolean()
#     is_validate_hatcher = fields.Boolean()
#
#
#     def action_validate(self):
#         user = self.env.user
#         for rec in self:
#             #todo
#             #nambahin stock, waktu validate
#
#             product_product_id = rec.product_product_id
#             if not product_product_id:
#                 raise ValidationError(_('Maaf, Produk harus dipilih dulu'))
#
#             if rec.fms_hatchery_hatcher_ids:
#                 model_stock_inventory = self.env['stock.inventory']
#                 model_stock_quant = self.env['stock.quant']
#                 model_stock_location = self.env['stock.location']
#                 operating_unit_id = rec.operating_unit_id
#                 stock_location_id = operating_unit_id.stock_location_id
#                 if not stock_location_id:
#                     raise ValidationError(_('Maaf, Lokasi default tidak ditemukan'))
#
#                 # rec_stock_quant = model_stock_quant.search([('product_id','=',product_product_id.id)], limit=1)
#                 # if rec_stock_quant:
#                 #     stock_location_id = rec_stock_quant.location_id
#                 # else:
#                 #     #todo cari default location_id
#                 #     rec_location = model_stock_location.search([('company_id', '=', user.company_id.id)], limit=1)
#                 #     if rec_location:
#                 #         stock_location_id = rec_location
#                 #     else:
#                 #         raise ValidationError(_('Maaf, Lokasi default tidak ditemukan'))
#
#                 vals = {
#                     "location_id": stock_location_id.id, #-------------------- stock.quant  where product_id = product.id -> return location_id.id
#                     "filter": "product",
#                     "company_id": user.company_id.id,
#                     "name": rec.display_name,
#                     "audit_period": False,
#                     "operating_unit_id": user.default_operating_unit_id.id,
#                     "flock_id": rec.flock_id.id,
#                     "accounting_date": False,
#                     "product_id": product_product_id.id,
#                     "category_id": False,
#                     "lot_id": False,
#                     "partner_id": False,
#                     "package_id": False,
#                     "exhausted": True,
#                 }
#                 rec_stock_inventory = model_stock_inventory.create(vals)
#                 rec_stock_inventory.action_start()
#
#                 for one_hatcher in rec.fms_hatchery_hatcher_ids:
#                     if one_hatcher.state != 'done':
#                         for one_inventory in rec_stock_inventory.line_ids:
#                             one_inventory.product_qty = one_inventory.product_qty + one_hatcher.salable_chick
#
#                 rec_stock_inventory.action_validate()
#
#             rec.state = 'done'
#             rec.fms_hatchery_setter_ids.write({'state': 'done'})
#             rec.fms_hatchery_hatcher_ids.write({'state': 'done'})
#
#             for one in rec.line_byproduct_ids_setter:
#                 if not one.is_done:
#                     one.do_move()
#
#             for one in rec.line_byproduct_ids_hatcher:
#                 if not one.is_done:
#                     one.do_move()
#
#     def action_validate_hatcher(self):
#         user = self.env.user
#         for rec in self:
#             product_product_id = rec.product_product_id
#             if not product_product_id:
#                 raise ValidationError(_('Maaf, Produk harus dipilih dulu'))
#
#             if rec.fms_hatchery_hatcher_ids:
#                 model_stock_inventory = self.env['stock.inventory']
#                 model_stock_quant = self.env['stock.quant']
#                 model_stock_location = self.env['stock.location']
#                 operating_unit_id = rec.operating_unit_id
#                 stock_location_id = operating_unit_id.stock_location_id
#                 if not stock_location_id:
#                     raise ValidationError(_('Maaf, Lokasi default tidak ditemukan'))
#
#                 # rec_stock_quant = model_stock_quant.search([('product_id','=',product_product_id.id)], limit=1)
#                 # if rec_stock_quant:
#                 #     stock_location_id = rec_stock_quant.location_id
#                 # else:
#                 #     #todo cari default location_id
#                 #     rec_location = model_stock_location.search([('company_id', '=', user.company_id.id)], limit=1)
#                 #     if rec_location:
#                 #         stock_location_id = rec_location
#                 #     else:
#                 #         raise ValidationError(_('Maaf, Lokasi default tidak ditemukan'))
#                 #
#                 # vals = {
#                 #     "location_id": stock_location_id.id, #-------------------- stock.quant  where product_id = product.id -> return location_id.id
#                 #     "filter": "product",
#                 #     "company_id": user.company_id.id,
#                 #     "name": rec.display_name,
#                 #     "audit_period": False,
#                 #     "operating_unit_id": user.default_operating_unit_id.id,
#                 #     "flock_id": rec.flock_id.id,
#                 #     "accounting_date": False,
#                 #     "product_id": product_product_id.id,
#                 #     "category_id": False,
#                 #     "lot_id": False,
#                 #     "partner_id": False,
#                 #     "package_id": False,
#                 #     "exhausted": True,
#                 # }
#                 # rec_stock_inventory = model_stock_inventory.create(vals)
#                 # rec_stock_inventory.action_start()
#                 #
#                 # for one_hatcher in rec.fms_hatchery_hatcher_ids:
#                 #     if one_hatcher.state != 'done':
#                 #         for one_inventory in rec_stock_inventory.line_ids:
#                 #             one_inventory.product_qty = one_inventory.product_qty + one_hatcher.salable_chick
#                 #
#                 # rec_stock_inventory.action_validate()
#             sum_use_qty = 0
#             for one in rec.fms_hatchery_hatcher_ids:
#                 sum_use_qty += one.he_received
#             sum_result = 0
#             for res in rec.line_byproduct_ids_hatcher:
#                 sum_result += res.qty
#
#             # validate setter proses dan setter result
#             if rec.total_setter_result != sum_use_qty:
#                 raise ValidationError(_('Quantity yang diproses tidak sama dengan Setter Result'))
#             if rec.total_setter_result != sum_result:
#                 raise ValidationError(_('Quantity result tidak sama dengan Setter Result'))
#
#             rec.state = 'done'
#             rec.is_validate_hatcher = True
#             rec.fms_hatchery_hatcher_ids.write({'state': 'done'})
#
#             for one in rec.line_byproduct_ids_hatcher:
#                 if not one.is_done:
#                     one.do_move()
#
#     @api.multi
#     def action_validate_setter(self):
#         for rec in self:
#             sum_use_qty = 0
#             for one in rec.fms_hatchery_setter_ids:
#                 sum_use_qty += one.total_he_received
#             sum_result = 0
#             for res in rec.line_byproduct_ids_setter:
#                 sum_result += res.qty
#
#             # validate setter proses dan setter result
#             if rec.he_qty != sum_use_qty:
#                 raise ValidationError(_('Quantity yang diproses tidak sama dengan HE Qty'))
#             if rec.he_qty != sum_result:
#                 raise ValidationError(_('Quantity result tidak sama dengan HE Qty'))
#
#             rec.state = 'done'
#             rec.is_validate_setter = True
#             rec.fms_hatchery_setter_ids.write({'state': 'done'})
#
#             for one in rec.line_byproduct_ids_setter:
#                 if not one.is_done:
#                     one.do_move()
#
#
#     @api.depends('work_order_id')
#     @api.onchange('work_order_id')
#     def onchange_work_order_id(self):
#         for rec in self:
#             work_order_id = rec.work_order_id
#             if work_order_id:
#                 if not rec.line_byproduct_ids_setter:
#                     hasil = []
#                     for one in work_order_id.line_byproduct_ids_setter:
#                         baru = [0, 0, {
#                             'fms_hatchery_id': rec.id,
#                             'product_product_id': one.product_product_id.id,
#                             'is_result': one.is_result,
#                             'qty': one.daily_target,
#                         }]
#                         hasil.append(baru)
#                     if hasil:
#                         rec.line_byproduct_ids_setter = hasil
#
#
#                 if not rec.line_byproduct_ids_hatcher:
#                     hasil = []
#                     for one in work_order_id.line_byproduct_ids_hatcher:
#                         baru = [0, 0, {
#                             'fms_hatchery_id': rec.id,
#                             'product_product_id': one.product_product_id.id,
#                             'is_result': one.is_result,
#                             'qty': one.daily_target,
#                         }]
#                         hasil.append(baru)
#                     if hasil:
#                         rec.line_byproduct_ids_hatcher = hasil
#
#
#
#     product_product_id_setter = fields.Many2one('product.product',string='Setter Result', related='work_order_id.product_product_id_setter')
#     planning_qty_setter = fields.Float(string='Setter Qty', related='work_order_id.planning_qty_setter')
#     uom_id_setter = fields.Many2one('uom.uom',string='Setter UOM', related='work_order_id.uom_id_setter')
#
#     product_product_id_hatcher = fields.Many2one('product.product',string='Hatcher Result', related='work_order_id.product_product_id_hatcher')
#     planning_qty_hatcher = fields.Float(string='Hatcher Qty', related='work_order_id.planning_qty_hatcher')
#     uom_id_hatcher = fields.Many2one('uom.uom',string='Hatcher UOM', related='work_order_id.uom_id_hatcher')
#
#     flock_id = fields.Many2one('berdikari.flock.master', string='Flock', related='work_order_id.flock_id', store=True)
#     house_id = fields.Many2one('berdikari.chicken.coop', string='House', related='work_order_id.house_id', store=True)
#     operating_unit_id = fields.Many2one('operating.unit', string='Unit', related='work_order_id.operating_unit_id', store=True)
#     def def_compute_unit_id(self):
#         for rec in self:
#             rec.unit_id = rec.operating_unit_id
#     unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)
#
#     #ini nggak dipakai
#     product_template_id = fields.Many2one('product.template', string='Breeding Result')
#     product_product_id = fields.Many2one('product.product', string='Breeding Result', related='work_order_id.product_product_id', store=True)
#
#     he_receive_qty = fields.Integer(string='HE Received QTY')
#     he_culling_qty = fields.Integer(string='HE Culling QTY')
#     he_qty = fields.Integer(string='HE QTY')
#
#     @api.onchange('he_receive_qty', 'he_culling_qty')
#     def hitung_he_qty(self):
#         for rec in self:
#             rec.he_qty = rec.he_receive_qty - rec.he_culling_qty
#             rec.hitung_qty_unused()
#
#     def hitung_qty_unused(self):
#         for rec in self:
#             total_setter_received = 0
#             for one in rec.fms_hatchery_setter_ids:
#                 total_setter_received += one.total_he_received
#
#             rec.he_qty_unused = rec.he_qty - total_setter_received
#     he_qty_unused = fields.Integer(string='Unused QTY')
#
#     body_weight = fields.Float()
#     uniformity = fields.Float()
#     notes = fields.Text()
#
#     file_name = fields.Char()
#
#     grading_flock_id = fields.Many2one('berdikari.flock.master', string='Flock')
#     grading_house_id = fields.Many2one('berdikari.chicken.coop', string='House')
#     grading_date_from = fields.Date(string='Date From')
#     grading_date_to = fields.Date(string='Date To')
#
#     setter_flock_id = fields.Many2one('berdikari.flock.master', string='Flock')
#     setter_house_id = fields.Many2one('berdikari.chicken.coop', string='House')
#     setter_date_from = fields.Date(string='Date From')
#     setter_date_to = fields.Date(string='Date To')
#
#     hatcher_flock_id = fields.Many2one('berdikari.flock.master', string='Flock')
#     hatcher_house_id = fields.Many2one('berdikari.chicken.coop', string='House')
#     hatcher_date_from = fields.Date(string='Date From')
#     hatcher_date_to = fields.Date(string='Date To')
#
#     state = fields.Selection([('draft', 'Draft'),('done', 'Done'),], default='draft')
#
#
#     # fms_hatchery_grading_ids = fields.One2many('berdikari.fms.hatchery.grading', 'fms_hatchery_id', string='FMS Hatchery Grading')
#     # fms_hatchery_grading_death_ids = fields.One2many('berdikari.fms.hatchery.grading.death', 'fms_hatchery_id', string='FMS Hatchery Grading / Death')
#     # fms_hatchery_grading_feed_ids = fields.One2many('berdikari.fms.hatchery.grading.feed', 'fms_hatchery_id', string='FMS Hatchery Grading / Feed')
#     # fms_hatchery_grading_byproduct_ids = fields.One2many('berdikari.fms.hatchery.grading.byproduct', 'fms_hatchery_id', string='FMS Hatchery Grading / By Product')
#     # fms_hatchery_grading_ovk_ids = fields.One2many('berdikari.fms.hatchery.grading.ovk', 'fms_hatchery_id', string='FMS Hatchery Grading / Other Material (OVK)')
#     #
#     # # fms_hatchery_detail = fields.One2many('berdikari.fms.hatchery.line', 'fms_hatchery_id', string='FMS Hatchery Detail')
#     # fms_hatchery_setter_received_ids = fields.One2many('berdikari.fms.hatchery.setter.received', 'fms_hatchery_id', string='FMS Hatchery Setter Received')
#     # fms_hatchery_setter_result_ids = fields.One2many('berdikari.fms.hatchery.setter.result', 'fms_hatchery_id', string='FMS Hatchery Setter Result')
#     # fms_hatchery_hatcher_received_ids = fields.One2many('berdikari.fms.hatchery.hatcher.received', 'fms_hatchery_id', string='FMS Hatchery Hatcher Received')
#     # fms_hatchery_hatcher_result_ids = fields.One2many('berdikari.fms.hatchery.hatcher.result', 'fms_hatchery_id', string='FMS Hatchery Hatcher Result')
#
#     # fms_hatchery_line2 = fields.One2many('berdikari.fms.hatchery.line', 'fms_hatchery_id')
#     # fms_hatchery_line3 = fields.One2many('berdikari.fms.hatchery.line', 'fms_hatchery_id')
#     # fms_hatchery_line4 = fields.One2many('berdikari.fms.hatchery.line', 'fms_hatchery_id')
#     # fms_hatchery_line5 = fields.One2many('berdikari.fms.hatchery.line', 'fms_hatchery_id')
#     # fms_hatchery_line6 = fields.One2many('berdikari.fms.hatchery.line', 'fms_hatchery_id')
#     # fms_hatchery_line7 = fields.One2many('berdikari.fms.hatchery.line', 'fms_hatchery_id')
#
#     fms_hatchery_detail = fields.Many2many('berdikari.fms.hatchery.line')
#     # fms_hatchery_setter_received_ids = fields.Many2many('berdikari.fms.hatchery.line')
#     fms_hatchery_hatcer_ids = fields.Many2many('berdikari.fms.hatchery.line')
#     fms_hatchery_line2 = fields.Many2many('berdikari.fms.hatchery.line')
#     fms_hatchery_line3 = fields.Many2many('berdikari.fms.hatchery.line')
#     fms_hatchery_line4 = fields.Many2many('berdikari.fms.hatchery.line')
#     fms_hatchery_line5 = fields.Many2many('berdikari.fms.hatchery.line')
#     fms_hatchery_line6 = fields.Many2many('berdikari.fms.hatchery.line')
#     fms_hatchery_line7 = fields.Many2many('berdikari.fms.hatchery.line')
#
#     breeding_input_id = fields.Many2one('berdikari.breeding.input')
#
#     @api.onchange('fms_hatchery_setter_ids')
#     def onchange_fms_hatchery_setter_ids(self):
#         for rec in self:
#             total = 0
#             for one in rec.fms_hatchery_setter_ids:
#                 total += one.total_he_received
#
#             total_unused = rec.he_receive_qty - rec.he_culling_qty
#             if total > total_unused:
#                 raise ValidationError(_('Qty Proses melebihi QTY Unused'))
#
#     fms_hatchery_setter_ids = fields.One2many('berdikari.fms.hatchery.setter', 'fms_hatchery_id', string='FMS Hatchery Setter')
#     fms_hatchery_hatcher_ids = fields.One2many('berdikari.fms.hatchery.hatcher', 'fms_hatchery_id', string='FMS Hatchery Hatcher')
#
#     total_hatcher_result = fields.Integer()
#
#     line_byproduct_ids_setter = fields.One2many('berdikari.fms.grading.setter.byproduct', 'fms_hatchery_id')
#     line_byproduct_ids_hatcher = fields.One2many('berdikari.fms.hatchery.byproduct.hatcher', 'fms_hatchery_id')
#
#     @api.onchange('line_byproduct_ids_setter')
#     def onchange_line_byproduct_ids_setter(self):
#         for rec in self:
#             total = 0
#             for one in rec.line_byproduct_ids_setter:
#                 if one.is_result:
#                     total += one.qty
#             rec.total_setter_result = total
#     total_setter_result = fields.Integer()
#
#     @api.onchange('line_byproduct_ids_hatcher')
#     def onchange_line_byproduct_ids_hatcher(self):
#         for rec in self:
#             total = 0
#             for one in rec.line_byproduct_ids_hatcher:
#                 if one.is_result:
#                     total += one.qty
#             rec.total_hatcher_result = total
#
#     @api.onchange('fms_hatchery_setter_ids')
#     def onchange_setter(self):
#         for rec in self:
#             # total = 0
#             # for one in rec.fms_hatchery_setter_ids:
#             #     total += one.fertile
#             # rec.total_setter_result = total
#             rec.hitung_qty_unused()
#
#     # @api.onchange('fms_hatchery_hatcher_ids')
#     # def onchange_hatcher(self):
#     #     for rec in self:
#     #         total = 0
#     #         for one in rec.fms_hatchery_hatcher_ids:
#     #             total += one.salable_chick
#     #         rec.total_hatcher_result = total
#
#     @api.model
#     def create(self, vals):
#         rec = super(FMSHatchery, self).create(vals)
#
#         if(rec.breeding_input_id):
#             rec.breeding_input_id.write({
#                 'fms_hatchery_id': rec.id,
#             })
#
#         return rec
#
#
# class FMSHatcheryDetail(models.Model):
#     _name = 'berdikari.fms.hatchery.line'
#
#     fms_hatchery_id = fields.Many2one('berdikari.fms.hatchery')
#     finished_goods = fields.Many2one('mrp.production')
#     flock = fields.Many2one('berdikari.flock.master')
#     work_center = fields.Selection([('grading','Grading'),('fumigasi','Fumigasi'),('prewarm','Prewarm'),('setter','Setter'),
#                                     ('transfer & carding','Transfer & Carding'),('pull chick','Pull Chick'),('packaging','Packaging')])
#     batch_id = fields.Char()
#     egg_use = fields.Boolean(string='Egg Use (Grading)')
#     egg_out_by_product = fields.Selection([('fumigasi','Fumigasi'),('prewarm','Prewarm'),('setter','Setter'),
#                                     ('transfer & carding','Transfer & Carding')])
#     other_material_code = fields.Char(string='Other Material Code (All WC)')
#     other_material_name = fields.Char(string='Other Material Name (All WC)')
#     other_material_qty = fields.Float()
#     machine_name = fields.Char(string='Machine Name (All WC)')
#     maching_hour = fields.Float(string='Machine Hour (All WC)')
#     doc_by_product = fields.Boolean(string='DOC By Product (Pull Chick)')
#     doc_in = fields.Boolean(string='DOC In (Packaging)')
#     # tab
#     manufacturing_order_id = fields.Char()
#
#
# class ByProductSetter(models.Model):
#     _name = 'berdikari.fms.grading.setter.byproduct'
#     _description = 'By Product - Setter'
#     _rec_name = 'product_product_id'
#
#     fms_hatchery_id = fields.Many2one('berdikari.fms.hatchery')
#
#     product_product_id = fields.Many2one('product.product', string="Product")
#     product_template_id = fields.Many2one('product.template', related='product_product_id.product_tmpl_id')
#     product_template_code = fields.Char(related='product_template_id.default_code')
#     uom_id = fields.Many2one('uom.uom', related='product_template_id.uom_id', store=True)
#     sex = fields.Selection([('male','Male'),('female','Female')], string='Sex', related='product_template_id.sex', store=True)
#     qty = fields.Float(string='Qty')
#     is_result = fields.Boolean(string='Is Result')
#
#     inv_transfer_id = fields.Char(string='Inv. Transfer ID')
#
#     #3 field ini di isi waktu do_move()
#     move_id = fields.Many2one('stock.move', 'Scrap Move', readonly=True)
#     location_id = fields.Many2one('stock.location', string='Location')
#     # lot_id = fields.Many2one('stock.production.lot', string='Lot/ Serial Number', related='location_id.lot_id')
#     lot_id = fields.Many2one('stock.production.lot', string='Lot/ Serial Number')
#
#     @api.multi
#     def do_move(self):
#         move = self.env['stock.move'].create(self._prepare_move_values())
#         move.with_context(is_scrap=True)._action_done()
#         self.write({'move_id': move.id, 'state': 'done'})
#         return True
#
#     def _prepare_move_values(self):
#         self.ensure_one()
#
#         product_product_id = self.product_product_id
#         product_template_id = self.product_template_id
#
#         # product_product_id = self.env['product.product'].search([('product_tmpl_id','=',product_template_id.id)], limit=1)
#         scrap_location_id = self.env['stock.location'].search([('scrap_location', '=', True), ('company_id', 'in', [self.env.user.company_id.id, False])], limit=1)
#         virtual_location_id = self.env.ref('stock.stock_location_stock')
#
#         stock_ids = self.env['stock.quant'].search([
#             ('product_id', '=', product_product_id.id),
#             ('company_id', '=', self.env.user.company_id.id),
#         ])
#
#         location_id = False
#         location_id_id = False
#         lot_id = False
#         stock_id = False
#         for one in stock_ids:
#             if one.quantity - one.reserved_quantity > 0:
#                 stock_id = one
#                 break
#
#         if stock_ids:
#             if not stock_id:
#                 stock_id = stock_ids[0]
#
#         if stock_id:
#             location_id = stock_id.location_id
#             location_id_id = location_id.id
#             lot_id = stock_id.lot_id
#
#         if not location_id:
#             location_id = virtual_location_id
#             location_id_id = virtual_location_id.id
#
#         partner_id = self.env.user.partner_id
#         qty = self.qty
#
#         value = qty * product_template_id.standard_price
#         value = 0
#
#         source_location = scrap_location_id
#         dest_location = location_id
#
#         result = {
#             'name': self.display_name,
#             'origin': self.fms_hatchery_id.display_name,
#             'product_id': product_product_id.id,
#             'product_uom': self.uom_id.id,
#
#             # 'product_qty': qty, #Jangan update field ini, gak boleh sama Odoo. ini sekarang compute. gantinya product_uom_qty
#             'product_uom_qty': qty,
#             'price_unit': product_template_id.lst_price,
#             'value': value,
#             'remaining_value': value,
#             'location_id': source_location.id,
#             'scrapped': False,
#             'location_dest_id': dest_location.id,
#             'move_line_ids': [(0, 0, {'product_id': product_product_id.id,
#                                            'product_uom_id': product_template_id.uom_id.id,
#                                            'qty_done': qty,
#                                            'location_id': source_location.id,
#                                            'location_dest_id': dest_location.id,
#                                            # 'package_id': self.package_id.id,
#                                            'owner_id': partner_id.id if partner_id else False,
#                                            'lot_id': lot_id.id if lot_id else False, })],
#             'restrict_partner_id': partner_id.id if partner_id else False,
#             'picking_id': False
#         }
#         return result
#
#
#     state = fields.Selection([('draft', '-'),('done', 'Done'),], default='draft')
#     def compute_is_done(self):
#         for rec in self:
#             rec.is_done = rec.state == 'done'
#     is_done = fields.Boolean(string='Done', compute=compute_is_done)
#
# class ByProductHatcher(models.Model):
#     _name = 'berdikari.fms.hatchery.byproduct.hatcher'
#     _description = 'By Product - Hatcher'
#     _rec_name = 'product_product_id'
#
#     fms_hatchery_id = fields.Many2one('berdikari.fms.hatchery')
#
#     product_product_id = fields.Many2one('product.product', string="Product")
#     product_template_id = fields.Many2one('product.template', related='product_product_id.product_tmpl_id')
#     product_template_code = fields.Char(related='product_template_id.default_code')
#     uom_id = fields.Many2one('uom.uom', related='product_template_id.uom_id', store=True)
#     sex = fields.Selection([('male','Male'),('female','Female')], string='Sex', related='product_template_id.sex', store=True)
#     qty = fields.Float(string='Qty')
#     is_result = fields.Boolean(string='Is Result')
#
#     inv_transfer_id = fields.Char(string='Inv. Transfer ID')
#
#     #3 field ini di isi waktu do_move()
#     move_id = fields.Many2one('stock.move', 'Scrap Move', readonly=True)
#     location_id = fields.Many2one('stock.location', string='Location')
#     # lot_id = fields.Many2one('stock.production.lot', string='Lot/ Serial Number', related='location_id.lot_id')
#     lot_id = fields.Many2one('stock.production.lot', string='Lot/ Serial Number')
#
#     @api.multi
#     def do_move(self):
#         move = self.env['stock.move'].create(self._prepare_move_values())
#         move.with_context(is_scrap=True)._action_done()
#         self.write({'move_id': move.id, 'state': 'done'})
#         return True
#
#     def _prepare_move_values(self):
#         self.ensure_one()
#
#         product_product_id = self.product_product_id
#         product_template_id = self.product_template_id
#
#         # product_product_id = self.env['product.product'].search([('product_tmpl_id','=',product_template_id.id)], limit=1)
#         scrap_location_id = self.env['stock.location'].search([('scrap_location', '=', True), ('company_id', 'in', [self.env.user.company_id.id, False])], limit=1)
#         virtual_location_id = self.env.ref('stock.stock_location_stock')
#
#         stock_ids = self.env['stock.quant'].search([
#             ('product_id', '=', product_product_id.id),
#             ('company_id', '=', self.env.user.company_id.id),
#         ])
#
#         location_id = False
#         location_id_id = False
#         lot_id = False
#         stock_id = False
#         for one in stock_ids:
#             if one.quantity - one.reserved_quantity > 0:
#                 stock_id = one
#                 break
#
#         if stock_ids:
#             if not stock_id:
#                 stock_id = stock_ids[0]
#
#         if stock_id:
#             location_id = stock_id.location_id
#             location_id_id = location_id.id
#             lot_id = stock_id.lot_id
#
#         if not location_id:
#             location_id = virtual_location_id
#             location_id_id = virtual_location_id.id
#
#         partner_id = self.env.user.partner_id
#         qty = self.qty
#
#         value = qty * product_template_id.standard_price
#         value = 0
#
#         source_location = scrap_location_id
#         dest_location = location_id
#
#         result = {
#             'name': self.display_name,
#             'origin': self.fms_hatchery_id.display_name,
#             'product_id': product_product_id.id,
#             'product_uom': self.uom_id.id,
#
#             # 'product_qty': qty, #Jangan update field ini, gak boleh sama Odoo. ini sekarang compute. gantinya product_uom_qty
#             'product_uom_qty': qty,
#             'price_unit': product_template_id.lst_price,
#             'value': value,
#             'remaining_value': value,
#             'location_id': source_location.id,
#             'scrapped': False,
#             'location_dest_id': dest_location.id,
#             'move_line_ids': [(0, 0, {'product_id': product_product_id.id,
#                                            'product_uom_id': product_template_id.uom_id.id,
#                                            'qty_done': qty,
#                                            'location_id': source_location.id,
#                                            'location_dest_id': dest_location.id,
#                                            # 'package_id': self.package_id.id,
#                                            'owner_id': partner_id.id if partner_id else False,
#                                            'lot_id': lot_id.id if lot_id else False, })],
#             'restrict_partner_id': partner_id.id if partner_id else False,
#             'picking_id': False
#         }
#         return result
#
#
#     state = fields.Selection([('draft', '-'),('done', 'Done'),], default='draft')
#     def compute_is_done(self):
#         for rec in self:
#             rec.is_done = rec.state == 'done'
#     is_done = fields.Boolean(string='Done', compute=compute_is_done)
