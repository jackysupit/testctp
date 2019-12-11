# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.jekdoo.utils.util import Util


class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _inherit = 'mail.thread'
    _description = 'Berdikari Purchase Request'

    name = fields.Char(string='Purchase Request Number', domain=[('invisible','=',True)])
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id, string='Requested By', readonly=True)
    employee_id = fields.Many2one('hr.employee',related='user_id.employee_id')
    # request_type = fields.Selection(selection=[('1', 'Umum'), ('2', 'Asset'), ('3', 'Operational')])

    @api.depends('user_id')
    @api.onchange('user_id')
    def compute_manager(self):
        for rec in self:
            rec.parent_id = False
            rec.user_parent_id = False
            if rec.employee_id and rec.employee_id.parent_id:
                rec.parent_id = rec.employee_id.parent_id.id
                rec.user_parent_id = rec.employee_id.parent_id.user_id
    parent_id = fields.Many2one('hr.employee', string='Manager', related='employee_id.parent_id')
    user_parent_id = fields.Many2one('res.users', string='Manager', related='parent_id.user_id')

    group_head_id = fields.Many2one('hr.employee', string='Group Head', related='parent_id.parent_id')
    user_group_head_id = fields.Many2one('res.users', string='Group Head', related='group_head_id.user_id')

    department_id = fields.Many2one('hr.department',string='Department', default=lambda self: self.env.user.employee_id.department_id)
    dest_department_id = fields.Many2one('hr.department',string='Department Type', domain=[('is_purchase_approval', '=', True)], track_visibility='onchange')
    job_id = fields.Many2one('hr.job',string='Position', related='employee_id.job_id')

    request_for_id = fields.Many2one('hr.employee',string='Request For')
    requisition_date = fields.Date(default=fields.Date.today, string='Date')

    requisition_deadline = fields.Date(string='Requisition Deadline')
    warehouse = fields.Many2one('stock.warehouse')
    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)

    def compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', default=lambda self:self.env.user.default_operating_unit_id, string="Unit", store=True, invisible=1, compute=compute_unit_id)

    remarks = fields.Text(string='Remarks')

    vendor_id = fields.Many2one('res.partner', domain=[('supplier','=',True),('is_company','=',True)])
    state= fields.Selection(
        [('draft','Draft'),('unit_head_approve', 'Unit Head Approved'),
        ('dept_head_approve','Dept Head Approved'),],string='State', default='draft',track_visibility='onchange')

    @api.depends('order_line')
    @api.onchange('order_line')
    def compute_req_type(self):
        for rec in self:
            is_stock = False
            for line in rec.order_line:
                if line.product_id.product_tmpl_id.type == 'consu' or line.product_id.product_tmpl_id.type == 'product':
                    is_stock = True
                    break
            rec.is_stock = is_stock
    is_stock = fields.Boolean(default=False,store=True)

    def compute_is_hide_confirm(self):
        for rec in self:
            is_hide = True
            if rec.state == 'draft' \
                    and (
                    self.env.ref('purchase.group_purchase_manager').id in self.env.user.groups_id.ids
                    and (rec.user_id.id == self.env.user.id or rec.user_parent_id.id == self.env.user.id)
            ):
                is_hide = False
            rec.is_hide_confirm = is_hide
    is_hide_confirm = fields.Boolean(compute=compute_is_hide_confirm, default=True)

    def compute_is_hide_approve(self):
        for rec in self:
            is_hide = True
            if rec.state == 'unit_head_approve' \
                and self.env.ref('purchase.group_purchase_manager').id in self.env.user.groups_id.ids \
                and (rec.user_group_head_id.id == self.env.user.id or rec.user_id.id == self.env.user.id):
                is_hide = False
            rec.is_hide_approve = is_hide
    is_hide_approve = fields.Boolean(compute=compute_is_hide_approve, default=True)

    def compute_is_hide_rfq(self):
        for rec in self:
            is_hide = True
            group_pengadaan_id = self.env.ref('berdikari.group_pengadaan')
            is_group_pengadaan = group_pengadaan_id.id in self.env.user.groups_id.ids
            # is_inventory = group_inventory_id.id in self.env.user.groups_id.ids
            # is_inventory_stock = is_inventory and rec.is_stock
            if rec.state == 'dept_head_approve' and is_group_pengadaan:
                is_hide = False
            rec.is_hide_rfq = is_hide
    is_hide_rfq = fields.Boolean(compute=compute_is_hide_rfq, default=True)

    def compute_is_hide_rfq_list(self):
        for rec in self:
            is_hide = True
            group_pengadaan_id = self.env.ref('berdikari.group_pengadaan')
            is_group_pengadaan = group_pengadaan_id.id in self.env.user.groups_id.ids
            if rec.state == 'dept_head_approve' and is_group_pengadaan:
                is_hide = False
            rec.is_hide_rfq_list = is_hide
    is_hide_rfq_list = fields.Boolean(compute=compute_is_hide_rfq_list, default=True)

    order_line = fields.One2many('purchase.request.line','request_id',string='Order Line')
    rfq_ids = fields.One2many('purchase.order', 'purchase_request_id', string='RFQ')
    def compute_count_rfq(self):
        for rec in self:
            rec.count_rfq = len(rec.rfq_ids)
    count_rfq = fields.Integer(compute=compute_count_rfq)

    @api.model_create_multi
    def create(self, vals_list):
        IrSequence = self.env['ir.sequence']
        name = IrSequence.next_by_code('purchase.request')
        vals_list[0]['name'] = name
        rec = super(PurchaseRequest, self).create(vals_list)
        return rec

    @api.multi
    def action_print_pr(self):
        pesan = 'File Printed'
        pesan += '\nNew Line'
        pesan += '<br/>new br'
        pesan += '\r\n new r new l'
        return Util.jek_pop1(_(pesan))

    def action_pr_submit(self):
        self.state = 'unit_head_approve'

    def action_pr_approve(self):
        self.state = 'dept_head_approve'

    @api.multi
    def action_create_rfq(self):
        ctx = {
            'default_purchase_request_id': self.id,
        }

        model_name = 'purchase.order'

        res_id = False
        action = Util.jek_open_form(
            self, model_name=model_name, id=res_id, ctx=ctx
        )
        return action

    # @api.multi
    # def action_female_employee(self):
    #     ctx = {
    #         'search_default_gender_female': True,
    #         'pr_name': self.name,
    #     }
    #     return Util.jek_redirect_to_model('hr.employee', 'female employee', ctx)

    @api.multi
    def action_rfq_list(self):
        ctx = {
            'search_default_purchase_request_id': self.name,
        }
        domain = [('purchase_request_id', '=', self.id)]

        return Util.jek_redirect_to_model('purchase.order', 'RFQ by PR Number', ctx, domain=domain)


class PurchaseRequestLine(models.Model):
    _name = 'purchase.request.line'
    _description = 'Berdikari Purchase Request Line'

    request_id = fields.Many2one('purchase.request')

    def default_product_product_ids(self):
        # import ipdb; ipdb.set_trace()
        ids = []
        ctx = self._context
        dest_department_id = ctx.get('dest_department_id')

        recs_product_categoryinfo = self.env['product.category'].search([('dest_department_id', '=', dest_department_id)])
        if recs_product_categoryinfo:
            for one in recs_product_categoryinfo:
                product_categ_id = one.id
                recs_product_tmpl = self.env['product.template'].search([('purchase_ok', '=', True), ('categ_id', '=', product_categ_id)])
                if recs_product_tmpl:
                    for prod in recs_product_tmpl:
                        recs_product_product = self.env['product.product'].search([('product_tmpl_id', '=', prod.id)])
                        if recs_product_product:
                            ids = ids + recs_product_product.ids
        return ids

    product_product_ids = fields.Many2many('product.product',
                                           string='Products List', default=default_product_product_ids)
    product_id = fields.Many2one('product.product', string='Product')

    @api.onchange('product_id')
    def _onchenge_product(self):
        self.description = self.product_id.name
    description = fields.Char()
    qty = fields.Float(string='Quantity')
    measure = fields.Many2one('uom.uom', string='UOM', related='product_id.uom_id', track_visibility='onchange')
    schedule_date = fields.Datetime(string='Schedule Date')