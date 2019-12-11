# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.template'
    _description = 'Inherit Product Template'

    name = fields.Char('Name', index=True, required=True, translate=True, track_visibility='onchange')
    product_scrap = fields.Boolean(string='Product Scrap')
    is_flock_material = fields.Boolean(string='Flock Material')
    sex = fields.Selection(selection=[
        ('male', 'Male'),
        ('female', 'Female'),
    ])

    @api.onchange('sex')
    def onchange_sex(self):
        domain = {}
        if self.sex:
            domain_asset_category_id = [('sex', '=', self.sex)]
        else:
            domain_asset_category_id = [('sex', '=', False)]

        domain['asset_category_id'] = domain_asset_category_id

        return {'domain': domain}

    uom_id = fields.Many2one('uom.uom')
    approval_state = fields.Selection(selection=[('draft', 'Draft'), ('inventory_confirm', 'Inventory Confirm'),
                                                 ('dh_inventory_approve', 'DH Inventory Approve'), ('tax_validation', 'Tax Validation'),
                                                 ('dh_tax_approve', 'DH Tax Approve')], default='draft')
    tax_validation_user_id = fields.Many2one('res.users')
    is_confirm = fields.Boolean(default=False)
    is_dept_head_approve = fields.Boolean(default=False)
    is_tax_validation = fields.Boolean(default=False)
    is_dh_tax_approve = fields.Boolean(default=False)

    def compute_is_hide_confirm(self):
        for rec in self:
            is_hide = True
            if rec.active:
                is_hide = True
            if rec.is_confirm == False:
                is_hide = False
            rec.is_hide_confirm = is_hide
    is_hide_confirm = fields.Boolean(compute=compute_is_hide_confirm, default=True)

    def compute_is_hide_inventory(self):
        for rec in self:
            is_hide = True
            group_inventory_id = self.env.ref('berdikari.group_inventory_dept_head_inventory')
            is_punya_hak = group_inventory_id.id in self.env.user.groups_id.ids
            if rec.is_confirm and is_punya_hak:
                is_hide = False
            if rec.is_dept_head_approve and is_punya_hak:
                is_hide = True
            rec.is_hide_inventory = is_hide
    is_hide_inventory = fields.Boolean(compute=compute_is_hide_inventory, default=True)

    def compute_is_hide_tax(self):
        for rec in self:
            is_hide = True
            group_tax_id = self.env.ref('berdikari.group_inventory_tax_validation')
            is_punya_hak = group_tax_id.id in self.env.user.groups_id.ids
            if rec.is_confirm and rec.is_dept_head_approve and is_punya_hak:
                is_hide = False
            if rec.is_tax_validation and is_punya_hak:
                is_hide = True
            rec.is_hide_tax = is_hide
    is_hide_tax = fields.Boolean(compute=compute_is_hide_tax, default=True)

    def compute_is_hide_dh_tax(self):
        for rec in self:
            is_hide = True
            is_punya_hak = False
            user_id = rec.tax_validation_user_id
            employee_id = user_id.employee_id
            parent_id = employee_id.parent_id
            user_parent_id = parent_id.user_id
            if user_parent_id.id == self.env.user.id:
                is_punya_hak = True
            if rec.is_confirm and rec.is_dept_head_approve and rec.is_tax_validation and is_punya_hak:
                is_hide = False
            if rec.is_dh_tax_approve and is_punya_hak:
                is_hide = True
            rec.is_hide_dh_tax = is_hide
    is_hide_dh_tax = fields.Boolean(compute=compute_is_hide_dh_tax, default=True)

    active = fields.Boolean(default=False)

    def action_confirm_product(self):
        self.approval_state = 'inventory_confirm'
        self.is_confirm = True

    def action_approve_dept_head(self):
        self.approval_state = 'dh_inventory_approve'
        self.is_dept_head_approve = True

    def action_tax_validate(self):
        self.tax_validation_user_id = self.env.user.id
        self.approval_state = 'tax_validation'
        self.is_tax_validation = True

    def action_dh_tax_approve(self):
        self.approval_state = 'dh_tax_approve'
        self.is_dh_tax_approve = True
        self.active = True

    @api.multi
    def copy(self, default=None):
        new_product = super(Product, self).copy(default=default)
        new_product.write({
            'approval_state': 'draft',
            'is_confirm': False,
            'is_dept_head_approve': False,
            'is_tax_validation': False,
            'is_dh_tax_approve': False,
            'active': False,
        })
        return new_product


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _description = 'Inherit Product Product'

    lot_id = fields.Many2many('stock.production.lot', string='Lot/ Serial Number')

    # modify
    # def action_view_stock_move_lines(self):
    #     self.ensure_one()
    #     action = self.env.ref('stock.stock_move_line_action').read()[0]
    #     action['domain'] = [('product_id.product_tmpl_id', 'in', self.ids)]
    #     return action


class ProductCategory(models.Model):
    _inherit = 'product.category'

    dest_department_id = fields.Many2one('hr.department',string='Department Type', domain=[('is_purchase_approval', '=', True)])


