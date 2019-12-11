# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleCouponProgram(models.Model):
    _inherit = 'sale.coupon.program'

    active = fields.Boolean(default=False)

    def action_approve(self):
        self.active = True


    def compute_is_hide_approve(self):
        for rec in self:
            is_hide = True
            group_sales_id = self.env.ref('berdikari.group_sale_dept_head')
            is_punya_hak = group_sales_id.id in self.env.user.groups_id.ids
            if is_punya_hak and rec.active == False:
                is_hide = False
            rec.is_hide_approve = is_hide
    is_hide_approve = fields.Boolean(compute=compute_is_hide_approve, default=True)
