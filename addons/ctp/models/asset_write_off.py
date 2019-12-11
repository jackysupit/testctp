# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AssetWriteOff(models.Model):
    _name = 'berdikari.asset.write.off'
    _description = 'Berdikari Asset Write Off'

    name = fields.Char(string='Number', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.write.off'), readonly=True)

    biologis_used_id = fields.Many2one('berdikari.asset.biologis.used')
    breeding_input_line_death_id = fields.Many2one('berdikari.breeding.input.line.death')

    #start related
    breeding_input_id = fields.Many2one('berdikari.breeding.input', related='breeding_input_line_death_id.breeding_input_id', store=True)
    work_order_id = fields.Many2one('berdikari.work.order', related='breeding_input_id.work_order_id', store=True)
    flock_id = fields.Many2one('berdikari.flock.master', related='work_order_id.flock_id', store=True)
    # purchase_id = fields.Char()

    purchase_id = fields.Many2one('purchase.order', related='flock_id.purchase_id', store=True)
    company_id = fields.Many2one('res.company', string='Company', related='flock_id.company_id', store=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)

    asset_id = fields.Many2one('account.asset.asset', related='breeding_input_line_death_id.asset_id', store=True, sting='Asset ID')
    asset_code = fields.Char(related='asset_id.code', string='Asset Name')
    asset_type = fields.Many2one('account.asset.category', related='asset_id.category_id')

    product_product_id = fields.Many2one('product.product', related='asset_id.product_product_id')
    asset_used_id = fields.Many2one('account.asset.asset.used')

    #end related

    date = fields.Date(default=fields.Date.today)
    asset_account = fields.Char()
    accum_asset_account = fields.Char(string='Accum. Asset Account')
    write_off_account = fields.Char()

    asset_qty = fields.Integer()
    write_off_qty = fields.Integer()
    aquire_value = fields.Integer(string='Total Acquire Value')
    accum_depr_value = fields.Integer(string='Total Accum Depr. Value')


    @api.depends('write_off_qty','asset_id')
    @api.onchange('write_off_qty','asset_id')
    def compute_write_off_value(self):
        for rec in self:
            rec.write_off_value = rec.write_off_qty * (rec.asset_id.value - rec.asset_id.current_depreciation_value)
    write_off_value = fields.Integer(string='Total Write Off Value', compute=compute_write_off_value, store=True)

    is_audit = fields.Boolean(string='Audit')
    notes = fields.Text()

    @api.model
    def create(self, vals):
        rec = super(AssetWriteOff, self).create(vals)

        rec.write(vals)

        asset_used_id = rec.asset_used_id
        print('############## AAAAAAAAAAAAAAAAAAAAAAA rec.write_off_qty: ', rec.write_off_qty)
        print('############## AAAAAAAAAAAAAAAAAAAAAAA asset_used_id.id: ', asset_used_id)
        print('############## AAAAAAAAAAAAAAAAAAAAAAA asset_used_id.qty: ', asset_used_id.qty)
        asset_used_id.write({
            'qty': asset_used_id.qty - rec.write_off_qty
        })
        print('############## BBBBBBBBBBBBBBBBBBBBBB asset_used_id.qty: ', asset_used_id.qty)

        return rec






