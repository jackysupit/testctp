# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"
    _description = 'Inherit Stock Picking Type'

    # picking_type_id = fields.Many2one('stock.picking.type', domain=lambda self: [('default_location_dest_id.company_id', '=', 'partner_id.company_id.id')])
    src_company_id = fields.Many2one('res.company', related='default_location_src_id.company_id', store=True)
    dest_company_id = fields.Many2one('res.company', related='default_location_dest_id.company_id', store=True)


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _description = 'Inherit Stock Picking'

    def _default_company_id(self):
        # company_id = self.env['res.company']._company_default_get('stock.picking')
        # if not company_id:
        #     id = self.env.user.company_id.id
        # else:
        #     id = company_id.id
        id = self.env.user.company_id.id
        return id

    company_id = fields.Many2one(
        'res.company', 'Company',
        default= lambda self: self.env.user.company_id.id,
        index=True, required=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    partner_company_id = fields.Many2one('res.company', related='partner_id.company_id', store=True, string="Partner - Company ID")
    dest_company_id = fields.Many2one('res.company', related='picking_type_id.dest_company_id', store=True, string="Dest - Company ID")
    operating_unit_id = fields.Many2one('operating.unit', related='location_dest_id.operating_unit_id', store=True, string="Unit")
    force_date = fields.Datetime('Force Date')
    is_force_date = fields.Boolean(related='company_id.is_force_date_stock')

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

    flock_id = fields.Many2one('berdikari.flock.master', related='purchase_id.flock_id')

    picking_type_id = fields.Many2one('stock.picking.type', domain="[('dest_company_id', '=', partner_company_id)]")

    def compute_type_inout(self):
        for rec in self:
            type_inout = 'in'
            if rec.picking_type_id and rec.picking_type_id.id == 2:
                type_inout = 'out'
            rec.type_inout = type_inout
    type_inout = fields.Selection([('in', 'IN'), ('out', 'Out')], string='Type In / Out', compute=compute_type_inout)

    @api.model
    def create(self, vals):
        params = self._context.get('params') or {}
        model = params.get('model') or ''

        origin = vals.get('origin')
        kode = ''
        if origin:
            kode = origin[:2]
        kode = kode.upper()

        company_id = 0
        operating_unit_id = 0
        dest_company_id = 0

        if kode == 'PO':
            location_dest_id = vals.get('location_dest_id')
            model_location = self.env['stock.location']
            location_dest = model_location.search([('id', '=', location_dest_id)])
            operating_unit_id = location_dest.operating_unit_id.id
            vals['operating_unit_id'] = operating_unit_id
        elif kode == 'SO':
            origin = vals.get('origin') or ''
            model_so = self.env['sale.order']
            if origin:
                rec = model_so.search([('name', '=', origin)])
                if rec:
                    # if rec.company_id.id == rec.warehouse_id.company_id.id:
                    #     vals['operating_unit_id'] = rec.warehouse_id.operating_unit_id.id
                    # else:
                    #     vals['operating_unit_id'] = rec.warehouse_id.operating_unit_id.id
                    company_id = rec.company_id.id
                    operating_unit_id = rec.warehouse_id.operating_unit_id.id
                    dest_company_id = rec.warehouse_id.company_id.id
                    vals['company_id'] = company_id
                    vals['operating_unit_id'] = operating_unit_id
                    vals['dest_company_id'] = dest_company_id

        ret = super(StockPicking, self).create(vals)
        if not ret.company_id:
            ret.company_id = company_id
        if not ret.operating_unit_id:
            ret.operating_unit_id = operating_unit_id
        if not ret.dest_company_id:
            ret.dest_company_id = dest_company_id

        return ret

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.picking_type_id = False

    @api.multi
    def action_done(self):
        ret = super(StockPicking, self).action_done()
        for rec in self:
            rec.update_po_line()
        return ret

    def update_po_line(self):
        origin = self.origin
        model_po = self.env['purchase.order']
        rec_po = model_po.search([('name', '=', origin)])
        if rec_po:
            move_line_ids = self.move_line_ids_without_package
            for one in move_line_ids:
                one_product_id = one.product_id
                one_qty = one.qty_done
                order_line = rec_po.order_line
                for line in order_line:
                    if line.product_id.id == one_product_id.id and (line.product_qty - line.qty_received > 0):
                        if (line.product_qty - line.qty_received) >= one_qty:
                            line.qty_received = line.qty_received + one_qty
                            one_qty = 0
                        else:
                            one_qty -= line.product_qty - line.qty_received
                            line.qty_received = line.qty_received + one_qty
                if one_qty:
                    one.qty_done -= one_qty

    @api.multi
    def action_done(self):
        print('Do something here sebelum validate')

        result = super(StockPicking, self).action_done()
        if self.force_date:
            self.write({'date_done': self.force_date})

        print('Do something here after validate')
        for rec in self:
            for line in rec.move_line_ids_without_package:

                product_product_id = line.product_id
                if not product_product_id.is_flock_material:
                    continue

                setup = self.env['jekdoo.setup'].get_setup()

                journal_id = setup.journal_asset_receipt_id

                if not journal_id:
                    raise ValidationError(_('Asset Receipt Journal is not set in Custom Setup'))

                debit_account_id = journal_id.default_debit_account_id
                credit_account_id = journal_id.default_credit_account_id

                if not debit_account_id:
                    raise ValidationError(_('Default Debit Account for Asset Receipt Journal is not set in Custom Setup'))

                if not credit_account_id:
                    raise ValidationError(_('Default Credit Account for Asset Receipt Journal is not set in Custom Setup'))

                qty = line.qty_done
                standard_price = product_product_id.standard_price
                value = qty * standard_price

                if not standard_price:
                    raise ValidationError(_('Cost Price is not set for product: {}'.format(product_product_id.display_name)))
                    # continue

                if not qty:
                    continue

                satu = {
                    'account_id': journal_id.id,
                    'operating_unit_id': rec.operating_unit_id.id,
                    # 'flock_id': rec.flock_id.id,
                    # 'currency_id': rec.currency_id.id,
                }

                satu_debit = satu.copy()
                satu_debit['account_id'] = debit_account_id.id
                satu_debit['debit'] = value

                satu_credit = satu.copy()
                satu_credit['account_id'] = credit_account_id.id
                satu_credit['credit'] = value

                flock_id = rec.flock_id

                vals_move = {
                    'date': rec.date,
                    'operating_unit_id': rec.operating_unit_id.id,
                    'journal_id': journal_id.id,
                    'flock_id': flock_id.id,
                    'journal_type': 'ASSET_RECEIPT',
                    'line_ids': [
                        (0, 0, satu_debit),
                        (0, 0, satu_credit)
                    ],
                }
                move = self.env['account.move']
                rec_move = move.create(vals_move)

                rec_move.post()


        model_asset = self.env['account.asset.asset']
        model_adding = self.env['berdikari.asset.adding']
        #1 create asset
        #2 create asset adding
        for rec in self:
            purchase_id = rec.purchase_id
            flock_id = purchase_id.flock_id
            #1 memastikan hanya jika flock saja, maka coding ini dijalankan
            if flock_id:
                for line in rec.move_ids_without_package: #model: stock.move

                    stock_move_line = self.env['stock.move.line'].search([('move_id', '=', line.id)], limit=1)

                    product_product_id = stock_move_line.product_id
                    product_template_id = line.product_id.product_tmpl_id

                    #2 pastikan, hanya jika productnya adalah Ayam / Flock Material
                    if product_template_id.is_flock_material:
                        asset_category_id = product_template_id.asset_category_id

                        uom_id = line.product_uom

                        # purchase_id = line.picking_id.purchase_id

                        # flock_id
                        # product_template_id
                        # receipt_ids
                        lot_id = stock_move_line.lot_id
                        lot_id_id = lot_id.id if lot_id else False
                        if lot_id_id:
                            record_asset = model_asset.search([('lot_id', '=', lot_id_id)], limit=1)
                        else:
                            record_asset = model_asset.search([('flock_id', '=', flock_id.id), ('product_template_id', '=', product_template_id.id)], limit=1)

                        if not record_asset:
                            vals = {
                                'name': "{} / {}".format(product_template_id.name, flock_id.name),
                                'code': "ASSET/{}".format(product_template_id.default_code),
                                'flock_id': flock_id.id,
                                'product_product_id': product_product_id.id,
                                'product_template_id': product_template_id.id,
                                'value': line.purchase_line_id.price_unit, #ini kosong untuk item yang ke-2
                                'salvage_value': 0,
                                # 'value_residual': 1,
                                'date': fields.Date.today(),
                                'qty_start': line.quantity_done,
                                # 'method_number': 18,  # perkiraan, 18 bulan
                                # 'method_period': 1,  # dalam 1 periode, ada berapa bulan? karena ini bulanan, ya 1
                                'sex': product_template_id.sex,
                                'uom_id': uom_id.id if uom_id else False,
                                'lot_id': stock_move_line.lot_id.id if stock_move_line.lot_id else False,
                                'location_id': rec.location_dest_id.id,
                                'picking_id': rec.id,
                                #todo: temporary hardcoded
                                # 'useful_life': 42,
                                # 'useful_life_unit': 'weeks',
                                # 'method_period': 1,
                                # 'method_period_unit': 'days',
                                # 'method_number': 294,
                                #fixing
                                'useful_life': asset_category_id.useful_life,
                                'useful_life_unit': asset_category_id.useful_life_unit,
                                'method_period': asset_category_id.method_period,
                                'method_period_unit': asset_category_id.method_period_unit,
                                'method_number': asset_category_id.method_number
                            }

                            if asset_category_id:
                                vals['category_id'] = asset_category_id.id

                            receipt_ids = [[0,0,{
                                'qty': line.quantity_done,
                                'receipt_id': line.id,
                                'purchase_line_id': line.purchase_line_id.id,
                            }]]
                            vals['receipt_ids'] = receipt_ids

                            record_asset = model_asset.create(vals)
                            line.asset_id = record_asset.id

                        else:
                            if lot_id:
                                if record_asset.product_id.id != product_product_id.id:
                                    raise ValidationError(_('Lot Number belongs to another product. {}'.format(lot_id.display_name)))


                            # record_asset = model_asset.create(vals)
                            vals = {
                                'qty_start': line.quantity_done + record_asset.qty_start,
                            }
                            receipt_ids = [[0,0,{
                                'qty': line.quantity_done,
                                'receipt_id': line.id,
                                'purchase_line_id': line.purchase_line_id.id,
                            }]]
                            vals['receipt_ids'] = receipt_ids

                            record_asset.write(vals)


                        if record_asset:
                            vals_adding = {
                                'asset_id': record_asset.id,
                                'asset_qty': record_asset.qty_start,
                                'uom_id': uom_id.id if uom_id else False,
                                'flock_id': flock_id.id,
                            }

                            asset_adding_detail = []
                            one_adding = {
                                'product_template_id': product_template_id.id,
                                'qty': record_asset.qty_start,
                                'uom_id': uom_id.id if uom_id else False,
                                'price': line.price_unit,
                                'amount': record_asset.qty_start * line.price_unit,
                            }

                            asset_adding_detail.append([0, 0, one_adding])

                            vals_adding['asset_adding_detail'] = asset_adding_detail

                            # vals_adding = {
                            #     'asset_id': record_asset.id,
                            #     'asset_qty': record_asset.qty_start,
                            #     'uom_id': uom_id.id if uom_id else False,
                            #     'flock_id': flock_id.id,
                            #     'asset_adding_detail': [
                            #         [0, 0, {
                            #                 'product_template_id': product_template_id.id,
                            #                 'qty': record_asset.qty_start,
                            #                 'uom_id': uom_id.id if uom_id else False,
                            #                 'price': line.price_unit,
                            #                 'amount': record_asset.qty_start * line.price_unit,
                            #             }],
                            #         [0, 0, {
                            #                 'product_template_id': product_template_id.id,
                            #                 'qty': record_asset.qty_start,
                            #                 'uom_id': uom_id.id if uom_id else False,
                            #                 'price': line.price_unit,
                            #                 'amount': record_asset.qty_start * line.price_unit,
                            #             }],
                            #         [0, 0, {
                            #                 'product_template_id': product_template_id.id,
                            #                 'qty': record_asset.qty_start,
                            #                 'uom_id': uom_id.id if uom_id else False,
                            #                 'price': line.price_unit,
                            #                 'amount': record_asset.qty_start * line.price_unit,
                            #             }],
                            #     ],
                            # }

                            record_adding = model_adding.create(vals_adding)

        return result

    # bikin juornal
    # @api.multi
    # def button_validate(self):
    #     total = 0
    #     for rec in self:
    #         for one in rec.move_ids_without_package:
    #             product_id = one.product_id
    #             qty = one.product_uom_qty
    #             for prod in product_id:
    #                 prod_tmp = prod.product_tmpl_id
    #                 for list in prod_tmp:
    #                     list_price = list.list_price
    #                     jml = list_price * qty
    #                     total = total + jml
    #     print('################ total: ', total)
    #
    #     model_account_move = self.env['account.move']
    #
    #     vals = {
    #         "date": fields.Date.today(),
    #         "journal_id": 43,
    #         "auto_reverse": False,
    #         "tax_type_domain": False,
    #         "ref": "TEST from validate internal transfer",
    #         "audit_period": False,
    #         "operating_unit_id": False,
    #         "line_ids": [
    #           [
    #             0,
    #             "virtual_1726",
    #             {
    #               "account_id": 4,
    #               "amount_currency": 0,
    #               "currency_id": 12,
    #               "debit": total,
    #               "credit": False,
    #               "tax_line_id": False,
    #               "partner_id": 1,
    #               "name": False,
    #               "analytic_account_id": False,
    #               "flocks": False,
    #               "analytic_tag_ids": [
    #                 [
    #                   6,
    #                   False,
    #                   []
    #                 ]
    #               ],
    #               "tax_ids": [
    #                 [
    #                   6,
    #                   False,
    #                   []
    #                 ]
    #               ],
    #               "date_maturity": False
    #             }
    #           ],
    #           [
    #             0,
    #             "virtual_1737",
    #             {
    #               "account_id": 4,
    #               "amount_currency": 0,
    #               "currency_id": 12,
    #               "debit": False,
    #               "credit": total,
    #               "tax_line_id": False,
    #               "partner_id": False,
    #               "name": False,
    #               "analytic_account_id": False,
    #               "flocks": False,
    #               "analytic_tag_ids": [
    #                 [
    #                   6,
    #                   False,
    #                   []
    #                 ]
    #               ],
    #               "tax_ids": [
    #                 [
    #                   6,
    #                   False,
    #                   []
    #                 ]
    #               ],
    #               "date_maturity": False
    #             }
    #           ]
    #         ]
    #     }
    #
    #     rec_account_move = model_account_move.create(vals)
    #     rec_account_move.action_post()
    #
    #
    #     return super(StockPicking, self).button_validate()