# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
from datetime import date, datetime, time
_logger = logging.getLogger(__name__)


class FMSGradingHatcher(models.Model):
    _name = 'berdikari.fms.grading.hatcher'
    _description = 'FMS Grading - Hatcher'

    name = fields.Char(string='Number', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.fms.hatchery'))
    date = fields.Date(default=lambda self: fields.Date.to_string(date.today()))
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    work_order_id = fields.Many2one('berdikari.work.order', string='Work Order ID')

    is_validated = fields.Boolean()

    def compute_is_invisible_validate_button(self):
        for rec in self:
            is_hide = True
            user = self.env.user
            if user and \
                user.employee_id and \
                user.employee_id.job_id and \
                user.employee_id.job_id.is_allow_validasi_hatcher:
                    is_hide = rec.is_validated
            rec.is_invisible_validate_button = is_hide
    is_invisible_validate_button = fields.Boolean(compute=compute_is_invisible_validate_button)

    def action_validate_hatcher(self):
        user = self.env.user
        for rec in self:
            product_product_id = rec.product_product_id
            if not product_product_id:
                raise ValidationError(_('Maaf, Produk harus dipilih dulu'))
            #
            # if rec.fms_hatchery_hatcher_ids:
            #     model_stock_inventory = self.env['stock.inventory']
            #     model_stock_quant = self.env['stock.quant']
            #     model_stock_location = self.env['stock.location']
            #     operating_unit_id = rec.operating_unit_id
            #     stock_location_id = operating_unit_id.stock_location_id
            #     if not stock_location_id:
            #         raise ValidationError(_('Maaf, Lokasi default tidak ditemukan'))
            #
            #     # rec_stock_quant = model_stock_quant.search([('product_id','=',product_product_id.id)], limit=1)
            #     # if rec_stock_quant:
            #     #     stock_location_id = rec_stock_quant.location_id
            #     # else:
            #     #     #todo cari default location_id
            #     #     rec_location = model_stock_location.search([('company_id', '=', user.company_id.id)], limit=1)
            #     #     if rec_location:
            #     #         stock_location_id = rec_location
            #     #     else:
            #     #         raise ValidationError(_('Maaf, Lokasi default tidak ditemukan'))
            #     #
            #     # vals = {
            #     #     "location_id": stock_location_id.id, #-------------------- stock.quant  where product_id = product.id -> return location_id.id
            #     #     "filter": "product",
            #     #     "company_id": user.company_id.id,
            #     #     "name": rec.display_name,
            #     #     "audit_period": False,
            #     #     "operating_unit_id": user.default_operating_unit_id.id,
            #     #     "flock_id": rec.flock_id.id,
            #     #     "accounting_date": False,
            #     #     "product_id": product_product_id.id,
            #     #     "category_id": False,
            #     #     "lot_id": False,
            #     #     "partner_id": False,
            #     #     "package_id": False,
            #     #     "exhausted": True,
            #     # }
            #     # rec_stock_inventory = model_stock_inventory.create(vals)
            #     # rec_stock_inventory.action_start()
            #     #
            #     # for one_hatcher in rec.fms_hatchery_hatcher_ids:
            #     #     if one_hatcher.state != 'done':
            #     #         for one_inventory in rec_stock_inventory.line_ids:
            #     #             one_inventory.product_qty = one_inventory.product_qty + one_hatcher.salable_chick
            #     #
            #     # rec_stock_inventory.action_validate()
            #
            sum_use_qty = 0
            for one in rec.line_ids:
                sum_use_qty += one.total_he_received

            sum_result = 0
            for res in rec.line_byproduct_ids_hatcher:
                sum_result += res.qty

            he_qty = rec.he_qty
            # validate hatcher proses dan hatcher result
            if int(sum_result) != int(sum_use_qty) and int(sum_result) != int(he_qty):
                raise ValidationError(_('Quantity yang diproses {} tidak sama dengan Result {} dan HE {}'.format(sum_use_qty, sum_result, he_qty)))

            rec.state = 'done'
            rec.is_validated = True

            for one in rec.line_byproduct_ids_hatcher:
                if not one.is_done:
                    one.do_move()

            rec.line_ids.write({'state': 'done'})
            rec.line_byproduct_ids_hatcher.write({'state': 'done'})


    @api.depends('work_order_id')
    @api.onchange('work_order_id')
    def onchange_work_order_id(self):
        for rec in self:
            work_order_id = rec.work_order_id
            if work_order_id:
                if not rec.line_byproduct_ids_hatcher:
                    hasil = []
                    for one in work_order_id.line_byproduct_ids_hatcher:
                        baru = [0, 0, {
                            'parent_id': rec.id,
                            'product_product_id': one.product_product_id.id,
                            # 'lot_id': one.lot_id.id,
                            'is_result': one.is_result,
                            'qty': one.daily_target,
                            'date': fields.Date.today(),
                        }]
                        hasil.append(baru)
                    if hasil:
                        rec.line_byproduct_ids_hatcher = hasil

                #
                # if not rec.line_byproduct_ids_hatcher:
                #     hasil = []
                #     for one in work_order_id.line_byproduct_ids_hatcher:
                #         baru = [0, 0, {
                #             'parent_id': rec.id,
                #             'product_product_id': one.product_product_id.id,
                #             'is_result': one.is_result,
                #             'qty': one.daily_target,
                #         }]
                #         hasil.append(baru)
                #     if hasil:
                #         rec.line_byproduct_ids_hatcher = hasil
                #
                #

    product_product_id_hatcher = fields.Many2one('product.product',string='Hatcher Result', related='work_order_id.product_product_id_hatcher')
    planning_qty_hatcher = fields.Float(string='Hatcher Qty', related='work_order_id.planning_qty_hatcher')
    uom_id_hatcher = fields.Many2one('uom.uom',string='Hatcher UOM', related='work_order_id.uom_id_hatcher')

    flock_id = fields.Many2one('berdikari.flock.master', string='Flock', related='work_order_id.flock_id', store=True)
    house_id = fields.Many2one('berdikari.chicken.coop', string='House', related='work_order_id.house_id', store=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Unit', related='work_order_id.operating_unit_id', store=True)
    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)

    #ini nggak dipakai
    product_template_id = fields.Many2one('product.template', string='Breeding Result')
    product_product_id = fields.Many2one('product.product', string='Breeding Result', related='work_order_id.product_product_id', store=True)

    he_receive_qty = fields.Integer(string='HE Received QTY')
    he_culling_qty = fields.Integer(string='HE Culling QTY')
    he_qty = fields.Integer(string='HE QTY')

    @api.onchange('he_receive_qty', 'he_culling_qty')
    def hitung_he_qty(self):
        for rec in self:
            rec.he_qty = rec.he_receive_qty - rec.he_culling_qty
            rec.hitung_qty_unused()

    def hitung_qty_unused(self):
        for rec in self:
            total_hatcher_received = 0
            for one in rec.line_ids:
                total_hatcher_received += one.total_he_received

            rec.he_qty_unused = rec.he_qty - total_hatcher_received
    he_qty_unused = fields.Integer(string='Unused QTY')

    body_weight = fields.Float()
    uniformity = fields.Float()
    notes = fields.Text()

    file_name = fields.Char()

    grading_flock_id = fields.Many2one('berdikari.flock.master', string='Flock')
    grading_house_id = fields.Many2one('berdikari.chicken.coop', string='House')
    grading_date_from = fields.Date(string='Date From')
    grading_date_to = fields.Date(string='Date To')

    hatcher_flock_id = fields.Many2one('berdikari.flock.master', string='Flock')
    hatcher_house_id = fields.Many2one('berdikari.chicken.coop', string='House')
    hatcher_date_from = fields.Date(string='Date From')
    hatcher_date_to = fields.Date(string='Date To')

    state = fields.Selection([('draft', 'Draft'),('done', 'Done'),], default='draft')


    # fms_hatchery_grading_ids = fields.One2many('berdikari.fms.hatchery.grading', 'parent_id', string='FMS Hatchery Grading')
    # fms_hatchery_grading_death_ids = fields.One2many('berdikari.fms.hatchery.grading.death', 'parent_id', string='FMS Hatchery Grading / Death')
    # fms_hatchery_grading_feed_ids = fields.One2many('berdikari.fms.hatchery.grading.feed', 'parent_id', string='FMS Hatchery Grading / Feed')
    # fms_hatchery_grading_byproduct_ids = fields.One2many('berdikari.fms.hatchery.grading.byproduct', 'parent_id', string='FMS Hatchery Grading / By Product')
    # fms_hatchery_grading_ovk_ids = fields.One2many('berdikari.fms.hatchery.grading.ovk', 'parent_id', string='FMS Hatchery Grading / Other Material (OVK)')
    #
    # # fms_hatchery_detail = fields.One2many('berdikari.fms.hatchery.line', 'parent_id', string='FMS Hatchery Detail')
    # fms_hatchery_hatcher_received_ids = fields.One2many('berdikari.fms.hatchery.hatcher.received', 'parent_id', string='FMS Hatchery Hatcher Received')
    # fms_hatchery_hatcher_result_ids = fields.One2many('berdikari.fms.hatchery.hatcher.result', 'parent_id', string='FMS Hatchery Hatcher Result')
    # fms_hatchery_hatcher_received_ids = fields.One2many('berdikari.fms.hatchery.hatcher.received', 'parent_id', string='FMS Hatchery Hatcher Received')
    # fms_hatchery_hatcher_result_ids = fields.One2many('berdikari.fms.hatchery.hatcher.result', 'parent_id', string='FMS Hatchery Hatcher Result')

    # fms_hatchery_line2 = fields.One2many('berdikari.fms.hatchery.line', 'parent_id')
    # fms_hatchery_line3 = fields.One2many('berdikari.fms.hatchery.line', 'parent_id')
    # fms_hatchery_line4 = fields.One2many('berdikari.fms.hatchery.line', 'parent_id')
    # fms_hatchery_line5 = fields.One2many('berdikari.fms.hatchery.line', 'parent_id')
    # fms_hatchery_line6 = fields.One2many('berdikari.fms.hatchery.line', 'parent_id')
    # fms_hatchery_line7 = fields.One2many('berdikari.fms.hatchery.line', 'parent_id')

    # fms_hatchery_detail = fields.Many2many('berdikari.fms.hatchery.line')
    # # fms_hatchery_hatcher_received_ids = fields.Many2many('berdikari.fms.hatchery.line')
    # fms_hatchery_hatcer_ids = fields.Many2many('berdikari.fms.hatchery.line')
    # fms_hatchery_line2 = fields.Many2many('berdikari.fms.hatchery.line')
    # fms_hatchery_line3 = fields.Many2many('berdikari.fms.hatchery.line')
    # fms_hatchery_line4 = fields.Many2many('berdikari.fms.hatchery.line')
    # fms_hatchery_line5 = fields.Many2many('berdikari.fms.hatchery.line')
    # fms_hatchery_line6 = fields.Many2many('berdikari.fms.hatchery.line')
    # fms_hatchery_line7 = fields.Many2many('berdikari.fms.hatchery.line')

    breeding_input_id = fields.Many2one('berdikari.breeding.input')

    @api.onchange('line_ids')
    def onchange_line_ids(self):
        for rec in self:
            total = 0
            for one in rec.line_ids:
                total += one.total_he_received

            total_unused = rec.he_receive_qty - rec.he_culling_qty
            if total > total_unused:
                raise ValidationError(_('Qty Proses melebihi QTY Unused'))

    line_ids = fields.One2many('berdikari.fms.grading.hatcher.line', 'parent_id', string='FMS Hatchery Hatcher')
    line_byproduct_ids_hatcher = fields.One2many('berdikari.fms.grading.hatcher.byproduct', 'parent_id')

    @api.onchange('line_byproduct_ids_hatcher')
    def onchange_line_byproduct_ids_hatcher(self):
        for rec in self:
            total = 0
            for one in rec.line_byproduct_ids_hatcher:
                if one.is_result:
                    total += one.qty
            rec.total_hatcher_result = total
    total_hatcher_result = fields.Integer()

    @api.onchange('line_ids')
    def onchange_hatcher(self):
        for rec in self:
            # total = 0
            # for one in rec.line_ids:
            #     total += one.fertile
            # rec.total_hatcher_result = total
            rec.hitung_qty_unused()

    # @api.onchange('fms_hatchery_hatcher_ids')
    # def onchange_hatcher(self):
    #     for rec in self:
    #         total = 0
    #         for one in rec.fms_hatchery_hatcher_ids:
    #             total += one.salable_chick
    #         rec.total_hatcher_result = total

    # @api.model
    # def create(self, vals):
    #     rec = super(FMSHatchery, self).create(vals)
    # 
    #     if(rec.breeding_input_id):
    #         rec.breeding_input_id.write({
    #             'parent_id': rec.id,
    #         })
    # 
    #     return rec

#
# class FMSGradingHatcherDetail(models.Model):
#     _name = 'berdikari.fms.grading.hatcher.line'
#
#     parent_id = fields.Many2one('berdikari.fms.grading.hatcher')
#     # parent_id = fields.Many2one('berdikari.fms.hatchery')
#     finished_goods = fields.Many2one('mrp.production')
#     flock = fields.Many2one('berdikari.flock.master')
#     work_center = fields.Selection([('grading','Grading'),('fumigasi','Fumigasi'),('prewarm','Prewarm'),('hatcher','Hatcher'),
#                                     ('transfer & carding','Transfer & Carding'),('pull chick','Pull Chick'),('packaging','Packaging')])
#     batch_id = fields.Char()
#     egg_use = fields.Boolean(string='Egg Use (Grading)')
#     egg_out_by_product = fields.Selection([('fumigasi','Fumigasi'),('prewarm','Prewarm'),('hatcher','Hatcher'),
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


class ByProductHatcher(models.Model):
    _name = 'berdikari.fms.grading.hatcher.byproduct'
    _description = 'By Product - Hatcher'
    _rec_name = 'product_product_id'

    parent_id = fields.Many2one('berdikari.fms.grading.hatcher')
    # parent_id = fields.Many2one('berdikari.fms.hatchery')
    date = fields.Date()

    product_product_id = fields.Many2one('product.product', string="Product")
    product_template_id = fields.Many2one('product.template', related='product_product_id.product_tmpl_id')
    product_template_code = fields.Char(related='product_template_id.default_code')
    uom_id = fields.Many2one('uom.uom', related='product_template_id.uom_id', store=True)
    sex = fields.Selection([('male','Male'),('female','Female')], string='Sex', related='product_template_id.sex', store=True)
    qty = fields.Float(string='Qty')
    is_result = fields.Boolean(string='Is Result')

    inv_transfer_id = fields.Char(string='Inv. Transfer ID')

    #3 field ini di isi waktu do_move()
    move_id = fields.Many2one('stock.move', 'Scrap Move', readonly=True)
    location_id = fields.Many2one('stock.location', string='Location')
    # lot_id = fields.Many2one('stock.production.lot', string='Lot/ Serial Number', related='location_id.lot_id')
    lot_id = fields.Many2one('stock.production.lot', string='Lot/ Serial Number')

    @api.multi
    def do_move(self):
        move = self.env['stock.move'].create(self._prepare_move_values())
        move.with_context(is_scrap=True)._action_done()
        self.write({'move_id': move.id, 'state': 'done'})
        return True

    def _prepare_move_values(self):
        self.ensure_one()

        product_product_id = self.product_product_id
        product_template_id = self.product_template_id

        # product_product_id = self.env['product.product'].search([('product_tmpl_id','=',product_template_id.id)], limit=1)
        scrap_location_id = self.env['stock.location'].search([('scrap_location', '=', True), ('company_id', 'in', [self.env.user.company_id.id, False])], limit=1)
        stock_location_id = self.env.ref('stock.stock_location_stock')

        stock_ids = self.env['stock.quant'].search([
            ('product_id', '=', product_product_id.id),
            ('company_id', '=', self.env.user.company_id.id),
        ])

        location_id = False
        location_id_id = False
        lot_id = False
        stock_id = False
        for one in stock_ids:
            if one.quantity - one.reserved_quantity > 0:
                stock_id = one
                break

        if stock_ids:
            if not stock_id:
                stock_id = stock_ids[0]

        if stock_id:
            location_id = stock_id.location_id
            location_id_id = location_id.id
            lot_id = stock_id.lot_id

        if not location_id:
            location_id = stock_location_id
            location_id_id = stock_location_id.id

        partner_id = self.env.user.partner_id
        qty = self.qty

        value = qty * product_template_id.standard_price
        value = 0

        source_location = scrap_location_id
        dest_location = location_id

        result = {
            'name': self.display_name,
            'origin': self.parent_id.display_name,
            'product_id': product_product_id.id,
            'product_uom': self.uom_id.id,

            # 'product_qty': qty, #Jangan update field ini, gak boleh sama Odoo. ini sekarang compute. gantinya product_uom_qty
            'product_uom_qty': qty,
            'price_unit': product_template_id.lst_price,
            'value': value,
            'remaining_value': value,
            'location_id': source_location.id,
            'scrapped': False,
            'location_dest_id': dest_location.id,
            'move_line_ids': [(0, 0, {'product_id': product_product_id.id,
                                           'product_uom_id': product_template_id.uom_id.id,
                                           'qty_done': qty,
                                           'location_id': source_location.id,
                                           'location_dest_id': dest_location.id,
                                           # 'package_id': self.package_id.id,
                                           'owner_id': partner_id.id if partner_id else False,
                                           'lot_id': lot_id.id if lot_id else False, })],
            'restrict_partner_id': partner_id.id if partner_id else False,
            'picking_id': False
        }
        print('################################################################# STOCK MOVE HATCHER: ', result)
        return result


    state = fields.Selection([('draft', '-'),('done', 'Done'),], default='draft')
    def compute_is_done(self):
        for rec in self:
            rec.is_done = rec.state == 'done'
    is_done = fields.Boolean(string='Done', compute=compute_is_done)


class FMSGradingHatcherLine(models.Model):
    _name = 'berdikari.fms.grading.hatcher.line'
    _description = 'FMS Hatchery Hatcher'

    # fms_hatchery_id = fields.Many2one('berdikari.fms.hatchery')
    parent_id = fields.Many2one('berdikari.fms.grading.hatcher')

    # name = fields.Char(string='Hatcher ID', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.fms.hatchery.hatcher'))
    name = fields.Char()
    product_product_id = fields.Many2one('product.product', 'Product')
    lot_id = fields.Many2one('stock.production.lot', 'Lot')

    date = fields.Date()
    farm = fields.Char(string='Farm/ Unit')
    hatcher_machine_id = fields.Many2one('berdikari.farm.machine', domain=[('type', '=', 'hatcher')], string=" Unit")
    capacity = fields.Integer(related='hatcher_machine_id.capacity')
    total_he_received = fields.Integer()
    total_he_culling = fields.Integer()
    total_he = fields.Integer()
    infertile = fields.Integer()
    explode = fields.Integer()
    fertile = fields.Integer()
    flock = fields.Many2one('berdikari.master.flock')

    state = fields.Selection([('draft', '-'),('done', 'Done'),], default='draft')
    def compute_is_done(self):
        for rec in self:
            rec.is_done = rec.state == 'done'
    is_done = fields.Boolean(string='Done', compute=compute_is_done)

    @api.onchange('total_he_received', 'total_he_culling', 'infertile', 'explode')
    def onchange_hitung_fertile(self):
        for rec in self:
            rec.total_he = rec.total_he_received - rec.total_he_culling
            rec.fertile = rec.total_he -rec.infertile - rec.explode

    @api.onchange('total_he_received')
    def onchange_hitung_fertile(self):
        for rec in self:
            if rec.capacity < rec.total_he_received:
                raise ValidationError(_('Over capacity'))
