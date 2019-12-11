# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo.addons.jekdoo.utils.util import Util


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    company = fields.Many2one('res.company', default=lambda self:self.env.user.company_id or self.env.user.default_operating_unit_id.company_id)
    audit_period = fields.Boolean(string='Audit Period')
    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)

    @api.onchange('operating_unit_id')
    def onchange_operating_unit_id(self):
        for rec in self:
            if rec.operating_unit_id:
                rec.location_id = rec.operating_unit_id.stock_location_id
                rec.company = rec.operating_unit_id.company_id

    def compute_my_location_ids(self):
        for rec in self:
            ids = []
            for one in self.env.user.operating_unit_ids:
                if one.stock_location_id:
                    # ids.append([6, 0, {'id':one.stock_location_id.id, 'location_id':one.stock_location_id.id, }])
                    # ids.append([6, 0, one.stock_location_id.id])
                    # satu = {'id': one.stock_location_id.id}
                    # ids.append([6, 0, satu])
                    # ids.append(one.stock_location_id)
                    ids.append(one.stock_location_id.id)
            rec.my_location_ids = ids

    def default_my_location_ids(self):
        ids = []
        for one in self.env.user.operating_unit_ids:
            if one.stock_location_id:
                ids.append(one.stock_location_id.id)
        return ids

    def domain_my_location_ids(self):
        domain = []
        ids = []
        for one in self.env.user.operating_unit_ids:
            if one.stock_location_id:
                ids.append(one.stock_location_id.id)

        domain = [('id', 'in', ids)]
        return domain

    my_location_ids = fields.Many2many('stock.location', 'stock_location_stock_scrap_rel', 'id', 'location_id'
                                       , compute=compute_my_location_ids
                                       , default=default_my_location_ids
                                       )

    location_id = fields.Many2one('stock.location', string='Location',
                                  default=lambda self: self.env.user.default_operating_unit_id.stock_location_id
                                  ,domain= domain_my_location_ids
                                  )

    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)

    flock_id = fields.Many2one('berdikari.flock.master')
    # product_id = fields.Many2one('product.template',string='Product')
    product_scrap = fields.Boolean(related='product_id.product_scrap', string='Product Scrap')

    stock_scrap_header_id = fields.Many2one('stock.scrap', string='Stock Scrap Header')


class StockScrapHeader(models.Model):
    _name = "berdikari.stock.scrap.header"
    _description = 'Stock Scrap tapi Header, stock.scrap asli jadi detail'

    name = fields.Char()
    company_id = fields.Many2one('res.company')
    operating_unit_id = fields.Many2one('operating.unit')
    stock_scrap_ids = fields.One2many('stock.scrap', 'stock_scrap_header_id', string='Scrap List')
    state = fields.Selection([('draft', 'Draft'),('done', 'Done'),], default='draft')

    @api.multi
    def action_validate(self):
        for rec in self:
            for one in rec.stock_scrap_ids:
                result = one.action_validate()
                if type(result) is not bool:
                    # {'name': 'Insufficient Quantity', 'view_type': 'form', 'view_mode': 'form',
                    #  'res_model': 'stock.warn.insufficient.qty.scrap', 'view_id': 1121, 'type': 'ir.actions.act_window',
                    #  'context': {'default_product_id': 176, 'default_location_id': 45, 'default_scrap_id': 14},
                    #  'target': 'new'}

                    name = result.get('name')

                    context = result.get('context')
                    default_product_id = context.get('default_product_id')
                    default_location_id = context.get('default_location_id')

                    product = self.env['product.product'].browse(default_product_id)
                    location_id = self.env['stock.location'].browse(default_location_id)

                    product_uom_id = one.product_uom_id

                    available_qty = 0
                    stock_quant = self.env['stock.quant'].search([('product_id','=',default_product_id),('location_id','=',default_location_id),('product_uom_id','=',product_uom_id.id)], limit=1)
                    other_stock = ''
                    if stock_quant:
                       available_qty = stock_quant.quantity
                    else:
                        stock_quant_ids = self.env['stock.quant'].search(
                            [('product_id', '=', default_product_id),
                             ('product_uom_id', '=', product_uom_id.id),
                             ('location_id.usage', '=', 'internal'),
                             ])
                        if stock_quant_ids:
                            other_stock += '\n---------------------------------------------------------------------'
                            for one_stock in stock_quant_ids:
                                other_stock += '\n Location: {} / {} {}'.format(one_stock.location_id.display_name, one_stock.quantity, one_stock.product_uom_id.display_name,)

                    pesan = _('{}: {} at {}, Available Stock: {} {}'.format(name, product.display_name, location_id.display_name, available_qty, other_stock))
                    return Util.jek_pop1(pesan, name)
                    # return result

            rec.name = self.env['ir.sequence'].next_by_code('berdikari.stock.scrap.header')
            rec.state = 'done'
        return True
