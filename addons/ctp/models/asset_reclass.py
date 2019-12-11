# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AssetReclass(models.Model):
    _name = 'berdikari.asset.reclass'
    _description = 'Berdikari Asset Reclass'

    number = fields.Char(string='Number')
    date = fields.Date()
    src_company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)
    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)



    @api.depends('operating_unit_id')
    @api.onchange('operating_unit_id')
    def onchange_unit_id(self):
        domain = {}
        operating_unit_id = self.operating_unit_id.id
        if operating_unit_id:
            domain_flock = [('operating_unit_id', '=', operating_unit_id)]
            domain['flock_id'] = domain_flock

        hasil = {'domain': domain}
        return hasil
    flock_id = fields.Many2one('berdikari.flock.master')
    is_audit = fields.Boolean(string='Audit')
    asset_id = fields.Many2one('account.asset.asset', string='Asset ID')
    asset_name = fields.Char(related='asset_id.code', string='Asset Name')
    asset_type = fields.Selection(related='asset_id.type', selection=[
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product')], string='Asset Type')
    asset_qty = fields.Integer()
    asset_account = fields.Char()
    asset_value = fields.Integer()
    total_asset_value = fields.Integer(readonly=True)
    remarks = fields.Text()

    reclass_asset_name = fields.Char()
    reclass_asset_type = fields.Char()
    reclass_asset_qty = fields.Integer()
    reclass_asset_account = fields.Char()