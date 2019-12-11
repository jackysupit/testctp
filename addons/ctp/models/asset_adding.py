# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AssetAdding(models.Model):
    _name = 'berdikari.asset.adding'
    _description = 'Berdikari Asset Adding'

    name = fields.Char(string='Number', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.asset.adding'))
    date = fields.Date(default=fields.Date.today())
    src_company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    is_audit = fields.Boolean(string='Audit')
    # asset_name = fields.Many2one('product.template')
    # asset_id = fields.Char(related='asset_name.default_code')
    asset_id = fields.Many2one('account.asset.asset', string='Asset ID', store=True)
    asset_name = fields.Char(related='asset_id.code', store=True, string='Asset Name')
    asset_account = fields.Char()

    # internal_reference = fields.Char(related='asset_id.code', string='Internaccount.asset.categoryal Reference')

    asset_type = fields.Selection(related='asset_id.type', selection=[
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product')], string='Asset Type')
    asset_qty = fields.Integer()
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure')

    notes = fields.Text()
    flock_id = fields.Many2one('berdikari.flock.master', readonly=True, related='asset_id.flock_id')

    # flock_id = fields.Many2one('berdikari.flock.master', readonly=True)
    # purchase_id = fields.Char()

    purchase_id = fields.Many2one('purchase.order', string='Purchase Order', related='flock_id.purchase_id')
    operating_unit_id = fields.Many2one('operating.unit', string=" Unit", related='flock_id.operating_unit_id')
    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)


    asset_adding_detail = fields.One2many('berdikari.asset.adding.line', 'asset_adding_id', string='Asset Adding Detail')
    asset_adding_aquire_ids = fields.One2many('berdikari.asset.adding.acquire', 'asset_adding_id')


class AssetAddingLine(models.Model):
    _name = 'berdikari.asset.adding.line'
    _description = 'Berdikari Asset Adding Line'

    asset_adding_id = fields.Many2one('berdikari.asset.adding')
    product_template_id = fields.Many2one('product.template')
    product_template_code = fields.Char(related='product_template_id.default_code')
    uom_id = fields.Many2one('uom.uom', related='product_template_id.uom_id', string='UOM')
    qty = fields.Integer()
    batch_id = fields.Char()
    price = fields.Float()


class AssetAddingAcquire(models.Model):
    _name = 'berdikari.asset.adding.acquire'
    _description = 'Berdikari Asset Adding Aquire'

    asset_adding_id = fields.Many2one('berdikari.asset.adding')
    description = fields.Char()
    amount = fields.Float()
    account = fields.Char() #ini mungkin harusnya Many2one ke ChartOfAccount