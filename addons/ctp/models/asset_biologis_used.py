# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

class AssetBiologisUsed(models.Model):
    _name = 'berdikari.asset.biologis.used'
    _description = 'Berdikari Asset Biologis Used'
    # _rec_name = 'house_id'

    name = fields.Char(string='Number', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.asset.biological'), readonly=True)
    date = fields.Date(default=fields.Date.today)
    work_order_id = fields.Many2one('berdikari.work.order')
    work_order_line_breed_id = fields.Many2one('berdikari.work.order.line.breed')
    company_id = fields.Many2one('res.company', read_only=1, related='work_order_id.company_id', store=True)
    operating_unit_id = fields.Many2one('operating.unit', string=" Unit", related='work_order_id.operating_unit_id', store=True)
    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)


    flock_id = fields.Many2one('berdikari.flock.master', related='work_order_id.flock_id', store=True)
    # house_id = fields.Many2one('berdikari.chicken.coop', related='work_order_id.house_id', store=True)
    house_id = fields.Many2one('berdikari.chicken.coop', related='work_order_line_breed_id.house_id', store=True)

    @api.onchange('work_order_id')
    def onchange_domain_asset_id(self):
        domain = {}
        product_template_ids = self.work_order_id.line_breed_ids.mapped('asset_id')
        if product_template_ids:
            domain['asset_id'] = [('id', 'in', product_template_ids.ids)]
            # singleton = 1 record
        return {'domain': domain}

    def domain_asset_id(self):
        domain = []
        product_template_ids = self.work_order_id.line_breed_ids.mapped('asset_id')
        if product_template_ids:
            domain = [('id', 'in', product_template_ids.ids)]
        return domain

    asset_id = fields.Many2one('account.asset.asset')
    asset_code = fields.Char(related='asset_id.code')
    asset_type = fields.Many2one('account.asset.category', related='asset_id.category_id')
    avail_qty = fields.Integer(related='asset_id.avail_qty', string="Unused Asset")

    asset_used_id = fields.Many2one('account.asset.asset.used')
    biologis_used_id = fields.Many2one('berdikari.asset.biologis.used')

    @api.onchange('wo_qty')
    def onchange_wo_qty(self):
        for rec in self:
            rec.asset_qty = rec.wo_qty

    asset_qty = fields.Integer(default=onchange_wo_qty) #asset yang digunakan
    sex = fields.Selection(related='asset_id.sex', readonly=True, store=True)

    wo_qty = fields.Integer(related='work_order_line_breed_id.planning_qty_line')
    last_qty = fields.Integer()

    @api.depends('add_ids')
    @api.onchange('add_ids')
    def compute_total_used(self):
        for rec in self:
            total_used = rec.asset_qty
            for one in rec.add_ids:
                total_used += one.qty

            rec.total_used = total_used

    total_used = fields.Integer(compute=compute_total_used, store=True)
    is_audit = fields.Boolean(string='Audit')
    notes = fields.Text()

    return_ids = fields.One2many('berdikari.asset.biologis.used.return', 'biologis_used_id')
    add_ids = fields.One2many('berdikari.asset.biologis.used.add', 'biologis_used_id')
    write_off_ids = fields.One2many('berdikari.asset.write.off', 'biologis_used_id')

    @api.model
    def create(self, vals):
        last_qty = vals.get('asset_qty')
        vals['last_qty'] = last_qty
        # vals['first_qty'] = vals.get('asset_qty')

        rec = super(AssetBiologisUsed, self).create(vals)

        rec.work_order_id.write({'biologis_used_id': rec.id})
        rec.work_order_line_breed_id.write({'biologis_used_id': rec.id})

        model_current_product = self.env['berdikari.work.order.line.current.product']

        vals_current_product = {
            'work_order_id': 0,
            'product_template_id': 0,
            'uom_id': 0,
            'qty': 0,
        }

        model_current_product.create(vals_current_product)


        #update Work Order
        if rec.sex == 'female':
            wo = rec.work_order_line_breed_id.work_order_id
            wo.write(
                {
                    'begin_qty_female': rec.last_qty,
                }
            )

        model_asset_used = self.env['account.asset.asset.used']
        rec_asset_used = model_asset_used.create({
            'asset_id': rec.asset_id.id,
            'biologis_used_id': rec.id,
            'first_qty': rec.asset_qty,
            'qty': rec.asset_qty,
            'date': rec.date,
        })
        rec.asset_used_id = rec_asset_used.id

        rec_breed_readonly = rec.work_order_line_breed_id

        model_breed = self.env['berdikari.work.order.line.breed']
        rec_breed = model_breed.browse(rec_breed_readonly.id)

        # print('AAAAAAAAAAAAAAAAAAAAA rec.asset_used_id', rec_breed.asset_used_id)
        # print('AAAAAAAAAAAAAAAAAAAAA rec.biologis_used_id', rec_breed.biologis_used_id)

        vals_breed = {
                'asset_used_id': rec_asset_used.id,
                'biologis_used_id': rec.id,
                'avail_qty': last_qty,
            }


        rec_breed.write(vals_breed)
        # print('BBBBBBBBBBBBBBBBBBBBBB vals_breed', vals_breed)
        # print('BBBBBBBBBBBBBBBBBBBBBB rec.asset_used_id', rec_breed.asset_used_id)
        # print('BBBBBBBBBBBBBBBBBBBBBB rec.biologis_used_id', rec_breed.biologis_used_id)

        return rec

    @api.depends('return_ids','add_ids','write_off_ids', 'asset_qty')
    @api.onchange('return_ids','add_ids','write_off_ids', 'asset_qty')
    def compute_qty(self):
        for rec in self:
            qty = rec.asset_qty
            for retur in rec.return_ids:
                qty -= retur.qty
            for write_off in rec.write_off_ids:
                qty -= write_off.qty

            for retur in rec.add_ids:
                qty += retur.qty
            rec.last_qty = qty


class AssetBiologisUsedReturn(models.Model):
    _name = 'berdikari.asset.biologis.used.return'
    _description = 'Berdikari Asset Biologis Used / Return'

    biologis_used_id = fields.Many2one('berdikari.asset.biologis.used')
    qty = fields.Integer()
    date = fields.Date(default=fields.Date.today)

    @api.model
    def create(self, vals):
        ret = super(AssetBiologisUsedReturn, self).create(vals)
        ret.biologis_used_id.compute_qty()
        return ret

    @api.multi
    def write(self, vals):
        ret = super(AssetBiologisUsedReturn, self).write(vals)
        for one in self:
            one.biologis_used_id.compute_qty()
        return ret


class AssetBiologisUsedAdd(models.Model):
    _name = 'berdikari.asset.biologis.used.add'
    _description = 'Berdikari Asset Biologis Used / Add'

    biologis_used_id = fields.Many2one('berdikari.asset.biologis.used')
    qty = fields.Integer()
    date = fields.Date(default=fields.Date.today)

    @api.model
    def create(self, vals):
        ret = super(AssetBiologisUsedAdd, self).create(vals)
        ret.biologis_used_id.compute_qty()
        return ret

    @api.multi
    def write(self, vals):
        ret = super(AssetBiologisUsedAdd, self).write(vals)
        for one in self:
            one.biologis_used_id.compute_qty()
        return ret

#
# class AssetBiologisUsedWriteOff(models.Model):
#     _name = 'berdikari.asset.biologis.used.write.off'
#     _description = 'Berdikari Asset Biologis Used / Write Off'
#
#     biologis_used_id = fields.Many2one('berdikari.asset.biologis.used')
#     qty = fields.Integer()
#     date = fields.Date(default=fields.Date.today)
#
#     @api.model
#     def create(self, vals):
#         ret = super(AssetBiologisUsedWriteOff, self).create(vals)
#         ret.biologis_used_id.compute_qty()
#         return ret
#
#     @api.multi
#     def write(self, vals):
#         ret = super(AssetBiologisUsedWriteOff, self).write(vals)
#         for one in self:
#             one.biologis_used_id.compute_qty()
#         return ret
