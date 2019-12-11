# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    _description = 'Inherit Stock Move Line'

    operating_unit_id = fields.Many2one('operating.unit', related='picking_id.operating_unit_id', store=True, string="Unit")
    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)



class StockMove(models.Model):
    _inherit = "stock.move"
    _description = 'Inherit Stock Move'

    # operating_unit_id = fields.Many2one('operating.unit', related='location_dest_id.company_id', store=True, string="Unit")
    operating_unit_id = fields.Many2one('operating.unit', related='picking_id.operating_unit_id', store=True, string="Unit")
    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)

    asset_id = fields.Many2one('account.asset.asset')

    flock_id = fields.Many2one('berdikari.flock.master')
    date = fields.Date()
    breeding_type = fields.Selection([('feed','Feed'),('ovk','OVK'),('feed2','Feed2'),('ovk2','OVK2'),])

    def _action_done(self):
        self.product_price_update_before_done()
        res = super(StockMove, self)._action_done()
        self._action_after_done(res)
        return res

    def _original_action_done(self):
        self.product_price_update_before_done()

        self.filtered(lambda move: move.state == 'draft')._action_confirm()  # MRP allows scrapping draft moves
        moves = self.exists().filtered(lambda x: x.state not in ('done', 'cancel'))
        moves_todo = self.env['stock.move']

        # Cancel moves where necessary ; we should do it before creating the extra moves because
        # this operation could trigger a merge of moves.
        for move in moves:
            if move.quantity_done <= 0:
                if float_compare(move.product_uom_qty, 0.0, precision_rounding=move.product_uom.rounding) == 0:
                    move._action_cancel()

        # Create extra moves where necessary
        for move in moves:
            if move.state == 'cancel' or move.quantity_done <= 0:
                continue
            # extra move will not be merged in mrp
            if not move.picking_id:
                moves_todo |= move
            moves_todo |= move._create_extra_move()

        # Split moves where necessary and move quants
        f_date = fields.Datetime.now()
        for move in moves_todo:
            # To know whether we need to create a backorder or not, round to the general product's
            # decimal precision and not the product's UOM.
            rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            if float_compare(move.quantity_done, move.product_uom_qty, precision_digits=rounding) < 0:
                # Need to do some kind of conversion here
                qty_split = move.product_uom._compute_quantity(move.product_uom_qty - move.quantity_done, move.product_id.uom_id, rounding_method='HALF-UP')
                new_move = move._split(qty_split)
                for move_line in move.move_line_ids:
                    if move_line.product_qty and move_line.qty_done:
                        # FIXME: there will be an issue if the move was partially available
                        # By decreasing `product_qty`, we free the reservation.
                        # FIXME: if qty_done > product_qty, this could raise if nothing is in stock
                        try:
                            move_line.write({'product_uom_qty': move_line.qty_done})
                        except UserError:
                            pass
                move._unreserve_initial_demand(new_move)
            if move.picking_id.force_date:
                f_date = move.picking_id.force_date
        moves_todo.mapped('move_line_ids')._action_done()
        # Check the consistency of the result packages; there should be an unique location across
        # the contained quants.
        for result_package in moves_todo\
                .mapped('move_line_ids.result_package_id')\
                .filtered(lambda p: p.quant_ids and len(p.quant_ids) > 1):
            if len(result_package.quant_ids.mapped('location_id')) > 1:
                raise UserError(_('You cannot move the same package content more than once in the same transfer or split the same package into two location.'))
        picking = moves_todo and moves_todo[0].picking_id or False
        moves_todo.write({'state': 'done', 'date': f_date})
        moves_todo.mapped('move_dest_ids')._action_assign()

        # We don't want to create back order for scrap moves
        # Replace by a kwarg in master
        if self.env.context.get('is_scrap'):
            return moves_todo

        if picking:
            picking._create_backorder()
        return moves_todo

    def _action_after_done(self, res):
        for move in res:
            # Apply restrictions on the stock move to be able to make
            # consistent accounting entries.
            if move._is_in() and move._is_out():
                raise UserError(_("The move lines are not in a consistent state: some are entering and other are leaving the company."))
            company_src = move.mapped('move_line_ids.location_id.company_id')
            company_dst = move.mapped('move_line_ids.location_dest_id.company_id')
            try:
                if company_src:
                    company_src.ensure_one()
                if company_dst:
                    company_dst.ensure_one()
            except ValueError:
                raise UserError(_("The move lines are not in a consistent states: they do not share the same origin or destination company."))

            #buang ini biar boleh intercompany
            # if company_src and company_dst and company_src.id != company_dst.id:
            #     raise UserError(_("The move lines are not in a consistent states: they are doing an intercompany in a single step while they should go through the intercompany transit location."))
            move._run_valuation()
        for move in res.filtered(lambda m: m.product_id.valuation == 'real_time' and (m._is_in() or m._is_out() or m._is_dropshipped() or m._is_dropshipped_returned())):
            move._account_entry_move()
        return res

    @api.model
    def create(self, vals):
        location_dest_id = vals.get('location_dest_id')
        model_location = self.env['stock.location']
        location_dest = model_location.search([('id', '=', location_dest_id)])
        operating_unit_id = location_dest.operating_unit_id.id
        vals['operating_unit_id'] = operating_unit_id
        ret = super(StockMove, self).create(vals)
        return ret

    def _get_price_unit(self):
        """ Returns the unit price for the move"""
        self.ensure_one()
        if self.purchase_line_id and self.product_id.id == self.purchase_line_id.product_id.id:
            line = self.purchase_line_id
            order = line.order_id
            price_unit = line.price_unit
            if line.taxes_id:
                price_unit = line.taxes_id.with_context(round=False).compute_all(price_unit, currency=line.order_id.currency_id, quantity=1.0)['total_excluded']
            if line.product_uom.id != line.product_id.uom_id.id:
                price_unit *= line.product_uom.factor / line.product_id.uom_id.factor
            if order.currency_id != order.company_id.currency_id:
                # override price get currency rate at force_date
                if self.picking_id.force_date:
                    date = self.picking_id.force_date
                else:
                    date = fields.Date.context_today(self)
                price_unit = order.currency_id._convert(price_unit, order.company_id.currency_id, order.company_id, date, round=False)
            return price_unit
        return super()._get_price_unit()


