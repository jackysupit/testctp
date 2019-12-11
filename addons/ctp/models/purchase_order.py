# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, tools
from odoo.addons.jekdoo.utils.util import Util


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    _description = 'Purchase Order'

    remarks = fields.Text()
    mode_of_payment = fields.Char()
    purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request Number')
    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id,
                                        )
    main_product_id = fields.Many2one('product.product', string='Main Product')

    # related = 'purchase_request_id.operating_unit_id'

    @api.onchange('purchase_request_id')
    def onchange_purchase_request_id(self):
        for rec in self:
            if rec.purchase_request_id and rec.purchase_request_id.operating_unit_id:
                rec.operating_unit_id = rec.purchase_request_id.operating_unit_id

    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id

    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)

    po_for = fields.Selection([('non flock', 'Non Flock'), ('flock', 'Flock')], string='Flock')
    flock_id = fields.Many2one('berdikari.flock.master', string='Flock')
    mode_of_payment_id = fields.Many2one('berdikari.mode.of.payment')
    rfq_name = fields.Char('RFQ Number', required=True, index=True, copy=False, default='New',
                           help="Unique number of the Request for Quotation number, "
                                "computed automatically when the Request for Quotation is created.")
    interchanging_rfq_sequence = fields.Char('Sequence')
    interchanging_po_sequence = fields.Char('Sequence')
    employee_id = fields.Many2one('hr.employee', related='user_id.employee_id')
    parent_id = fields.Many2one('hr.employee', string='Manager', related='employee_id.parent_id')
    user_parent_id = fields.Many2one('res.users', string='Manager', related='parent_id.user_id')
    group_head_id = fields.Many2one('hr.employee', string='Group Head', related='parent_id.parent_id')
    user_group_head_id = fields.Many2one('res.users', string='Group Head', related='group_head_id.user_id')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            name = self.env['ir.sequence'].next_by_code('purchase.order.quotation') or 'New'
            vals['rfq_name'] = vals['name'] = name

        rec = super(PurchaseOrder, self).create(vals)
        rec.flock_id.write({
            'purchase_id': rec.id,
        })

        return rec

    @api.multi
    def button_draft(self):
        res = super(PurchaseOrder, self).button_draft()
        if self.interchanging_rfq_sequence:
            self.write({'interchanging_po_sequence': self.name})
            self.write({'name': self.interchanging_rfq_sequence})

        return res

    @api.multi
    def copy(self, default=None):
        new_po = super(PurchaseOrder, self).copy(default=default)
        new_po.write({
            'is_confirm_inventory': False,
            'is_confirm_pengadaan': False,
        })
        return new_po

    @api.depends('order_line')
    @api.onchange('order_line')
    def compute_hide_confirm_inventory2(self):
        for rec in self:
            is_hide = True
            is_contain_stock = False
            is_stock = False
            for line in rec.order_line:
                if not is_contain_stock:
                    if line.product_id.product_tmpl_id.type == 'consu' or line.product_id.product_tmpl_id.type == 'product':
                        is_stock = True
                    if is_stock:
                        is_contain_stock = True
                        break

            if is_contain_stock:
                # for rec in self:
                is_hide = True
                group_inventory_id = self.env.ref('berdikari.group_purchase_validasi_inventory')
                is_punya_hak = group_inventory_id.id in self.env.user.groups_id.ids

                if is_punya_hak:
                    if not rec.is_confirm_inventory: #ini yakin not ya?
                        is_hide = False

            else:
                is_hide = True
            rec.is_hide_confirm_inventory = is_hide

    is_not_stock = fields.Boolean(compute=compute_hide_confirm_inventory2, store=True)

    is_hide_confirm_inventory = fields.Boolean(compute=compute_hide_confirm_inventory2)
    is_confirm_inventory = fields.Boolean(string='Confirm By Inventory')

    def button_confirm_inventory(self):
        self.is_confirm_inventory = True

    def compute_hide_confirm_pengadaan(self):
        for rec in self:
            is_hide = True
            if not rec.is_confirm_pengadaan:
                if rec.state == 'draft' and self.env.ref(
                        'berdikari.group_purchase_validasi_pengadaan').id in self.env.user.groups_id.ids:
                    is_hide = False
                    if not rec.is_not_stock and not rec.is_confirm_inventory:
                        is_hide = True
            rec.is_hide_confirm_pengadaan = is_hide

    is_hide_confirm_pengadaan = fields.Boolean(compute=compute_hide_confirm_pengadaan, default=True)
    is_confirm_pengadaan = fields.Boolean(string='Confirm By Pengadaan')

    def button_confirm_pengadaan(self):
        self.write({'is_confirm_pengadaan': True, })

    def compute_hide_approve_dept_head(self):
        for rec in self:
            is_hide = True
            if not rec.is_approve_dept_head:
                if rec.state == 'draft' and (
                        rec.user_id.id == self.env.user.id or rec.user_parent_id.id == self.env.user.id):
                    if rec.is_not_stock:
                        if rec.is_confirm_pengadaan:
                            is_hide = False
                    else:
                        if rec.is_confirm_inventory and rec.is_confirm_pengadaan:
                            is_hide = False
            rec.is_hide_approve_dept_head = is_hide

    is_hide_approve_dept_head = fields.Boolean(compute=compute_hide_approve_dept_head, default=True)
    is_approve_dept_head = fields.Boolean(string='Dept Head Approved')

    def compute_is_debug(self):
        for rec in self:
            rec.is_debug = False

    is_debug = fields.Boolean(compute=compute_is_debug)

    def button_approve_dept_head(self):
        self.write({'is_approve_dept_head': True, 'state': 'to approve'})

    def compute_hide_approve_group_head(self):
        for rec in self:
            is_hide = True
            if not rec.is_approve_group_head:
                if rec.state == 'to approve' and (
                        rec.user_id.id == self.env.user.id or rec.user_group_head_id.id == self.env.user.id):
                    if rec.is_not_stock:
                        if rec.is_confirm_pengadaan and rec.is_approve_dept_head:
                            is_hide = False
                    else:
                        if rec.is_confirm_inventory and rec.is_confirm_pengadaan and rec.is_approve_dept_head:
                            is_hide = False
            rec.is_hide_approve_group_head = is_hide

    is_hide_approve_group_head = fields.Boolean(compute=compute_hide_approve_group_head, default=True)
    is_approve_group_head = fields.Boolean(string='Group Head Approved')

    def button_approve_group_head(self):
        # set po number
        # number = False
        # po_number = False
        # last_number = self.env['purchase.order'].search([('state', '=', 'purchase')], order='name desc', limit=1)
        # if last_number.po_number:
        #     number = last_number.po_number
        # else:
        #     number = last_number.name
        #
        # if number:
        #     number = number[2:7]
        #     number = int(number)
        #     number = number + 1
        #     number = str(number)
        #     if len(number) == 1:
        #         po_number = 'PO0000' + number
        #     elif len(number) == 2:
        #         po_number = 'PO000' + number
        #     elif len(number) == 3:
        #         po_number = 'PO00' + number
        #     elif len(number) == 4:
        #         po_number = 'PO0' + number
        #     elif len(number) == 5:
        #         po_number = 'PO' + number
        # else:
        #     po_number = 'PO00001'

        self.write({'is_approve_group_head': True})
        res = super(PurchaseOrder, self).button_approve()
        for order in self:
            if order.interchanging_rfq_sequence:
                order.write({'name': order.interchanging_po_sequence})
            else:
                new_name = self.env['ir.sequence'].next_by_code('purchase.order') or '/'
                order.write({'interchanging_rfq_sequence': order.name})
                order.write({'name': new_name})
            self.picking_ids.write({'origin': order.interchanging_po_sequence})
            if self.picking_ids:
                for pick in self.picking_ids:
                    pick.move_lines.write({'origin': order.interchanging_po_sequence})
        return res

        # if self.is_not_stock or self.is_confirm_inventory:
        #     return super(PurchaseOrder, self).button_approve()

    @api.multi
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.interchanging_rfq_sequence:
                order.write({'name': order.interchanging_po_sequence})
            else:
                new_name = self.env['ir.sequence'].next_by_code('purchase.order') or '/'
                order.write({'interchanging_rfq_sequence': order.name})
                order.write({'name': new_name})
            self.picking_ids.write({'origin': order.interchanging_po_sequence})
            if self.picking_ids:
                for pick in self.picking_ids:
                    pick.move_lines.write({'origin': order.interchanging_po_sequence})
        return res

    # def button_confirm(self):
    #     if self.is_confirm_inventory and self.is_confirm_pengadaan:
    #         return super(PurchaseOrder, self).button_confirm()
    #     else:
    #         return Util.jek_pop1(_('Harus Confirm Pengadaan dan Inventory dulu'))

    @api.depends('purchase_request_id')
    @api.onchange('purchase_request_id')
    def onchange_purchase_request_id(self):
        for rec in self:
            pr_id = rec.purchase_request_id
            if pr_id:
                if not rec.order_line:
                    hasil = []
                    for one in pr_id.order_line:
                        baru = [0, 0, {
                            'order_id': rec.id,
                            'product_id': one.product_id,
                            'name': one.description,
                            'product_qty': one.qty,
                            'product_uom': one.measure,
                            'date_planned': one.schedule_date,
                        }]
                        hasil.append(baru)
                    if hasil:
                        rec.order_line = hasil

    dest_department_id = fields.Many2one('hr.department', string='Department Type',
                                         related='purchase_request_id.dest_department_id')
    product_ids = fields.One2many('product.supplierinfo', 'name', string='Products', related='partner_id.product_ids')

    def default_amount_inv(self):
        for rec in self:
            is_hide = False
            group_inventory_id = self.env.ref('berdikari.group_purchase_validasi_inventory')
            is_inventory = group_inventory_id.id in self.env.user.groups_id.ids
            if is_inventory:
                is_hide = True
            rec.is_hide_amount_for_inventory = is_hide

    is_hide_amount_for_inventory = fields.Boolean(compute=default_amount_inv)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _description = 'inherit Purchase Order Line'

    operating_unit_id = fields.Many2one('operating.unit', related='order_id.operating_unit_id', string=" Unit",
                                        store=True)

    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id

    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)
    note = fields.Text()
    available_qty = fields.Float(related='product_id.qty_available')

    def default_value_inv(self):
        for rec in self:
            #INI KEBALIK KALI YA? - jacky
            #tidak kebalik, karena untuk hide unit price, tax dan total price saat staff inventory login
            is_hide = False
            group_inventory_id = self.env.ref('berdikari.group_purchase_validasi_inventory')
            is_inventory = group_inventory_id.id in self.env.user.groups_id.ids
            if is_inventory:
                is_hide = True
            rec.is_hide_for_inventory = is_hide

    is_hide_for_inventory = fields.Boolean(compute=default_value_inv)

    received_qty = fields.Integer()
    billed_qty = fields.Integer()

    color = fields.Char(string='Color')

    # def default_product_tmpl_ids(self):
    #     ids = []
    #     ctx = self._context
    #     parent_partner_id = ctx.get('parent_partner_id')
    #
    #     recs_product_supplierinfo = self.env['product.supplierinfo'].search([('name','=',parent_partner_id)])
    #     if recs_product_supplierinfo:
    #         for one in recs_product_supplierinfo:
    #             ids.append(one.product_tmpl_id.id)
    #     return ids

    def default_product_product_ids(self):
        ids = []
        ctx = self._context
        parent_partner_id = ctx.get('parent_partner_id')

        recs_product_supplierinfo = self.env['product.supplierinfo'].search([('name', '=', parent_partner_id)])
        if recs_product_supplierinfo:
            for one in recs_product_supplierinfo:
                product_tmpl_id = one.product_tmpl_id.id
                recs_product_product = self.env['product.product'].search([('product_tmpl_id', '=', product_tmpl_id)])
                if recs_product_product:
                    ids = ids + recs_product_product.ids
        return ids

    # product_template_ids = fields.Many2many('product.template', 'id', string='Products List', default=default_product_tmpl_ids)
    product_product_ids = fields.Many2many('product.product', 'purchase_order_line_product_rel', 'id', 'product_id',
                                           string='Products List', default=default_product_product_ids)

class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    operating_unit_id = fields.Many2one('operating.unit', string='Unit')
    date_planned = fields.Datetime(string='Scheduled Date')
    purchase_request_id = fields.Many2one('purchase.request', string='Reference')
    name = fields.Char(string='Bill Reference')
    amount_untaxed = fields.Float(string='Untaxed Amount')


    def _select(self):
        return super(PurchaseReport, self)._select() + ", ou.id as operating_unit_id, s.date_planned as date_planned, s.name"\
                                                        ", s.purchase_request_id, s.amount_untaxed"

    def _from(self):
        return super(PurchaseReport, self)._from() + " left join operating_unit ou on ou.id = s.operating_unit_id"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", ou.id, s.date_planned, s.name, s.purchase_request_id, s.amount_untaxed"

