# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Receipts(models.Model):
    _inherit = 'stock.picking'
    _description = 'Inherit Stock Picking'

    audit_period = fields.Boolean(string='Audit Period')


class InventoryAdjustment(models.Model):
    _name = 'stock.inventory'
    _inherit = ['stock.inventory', 'mail.thread']
    _description = 'Inherit Stock inventory'

    audit_period = fields.Boolean(string='Audit Period')
    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)

    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)


    flock_id = fields.Many2one('berdikari.flock.master')
    is_flock_material = fields.Boolean(related='product_id.product_tmpl_id.is_flock_material')


    def default_dept_head_keuangan_id(self):
        dept_head_keuangan_id = False
        model_employee = self.env['hr.employee']
        setup = self.env['jekdoo.setup'].get_setup()
        dept_list = False
        # import pdb; pdb.set_trace()
        try:
            if hasattr(setup, 'dept_keuangan_id'):
                dept_list = setup.dept_keuangan_id
        except:
            print('Dept Keuangan belum di-set di Configuration')
        if not dept_list:
            return False

        job_list = setup.job_dept_head_keuangan_id
        if dept_list or job_list:
            emp_id = model_employee.search([('department_id', '=', dept_list.id), ('job_id', '=', job_list.id)], limit=1)
            dept_head_keuangan_id = emp_id.id

        return dept_head_keuangan_id
    dept_head_keuangan_id = fields.Many2one('hr.employee', default=default_dept_head_keuangan_id)


    def default_dept_head_akuntansi_id(self):
        dept_head_akuntansi_id = False
        model_employee = self.env['hr.employee']
        setup = self.env['jekdoo.setup'].get_setup()
        dept_list = False
        job_list = False

        try:
            if hasattr(setup, 'dept_akuntansi_id'):
                dept_list = setup.dept_akuntansi_id

            if hasattr(setup, 'job_dept_head_akuntansi_id'):
                job_list = setup.job_dept_head_akuntansi_id

        except:
            print('Dept Keuangan & Job Dept Head Keuangan belum di-set di Configuration')
        if not dept_list:
            return False

        if dept_list or job_list:
            emp_id = model_employee.search([('department_id', '=', dept_list.id), ('job_id', '=', job_list.id)], limit=1)
            dept_head_akuntansi_id = emp_id.id

        return dept_head_akuntansi_id
    dept_head_akuntansi_id = fields.Many2one('hr.employee', default=default_dept_head_akuntansi_id)


class InventoryAdjustmentLine(models.Model):
    _inherit = 'stock.inventory.line'
    _description = 'Inherit Stock Inventory Line'


    @api.depends('product_qty')
    @api.onchange('product_qty')
    def onchange_product_qty(self):
        difference_qty = self.theoretical_qty - self.product_qty
        self.difference_qty = difference_qty
    difference_qty = fields.Integer()


# class InventoryLandedCosts(models.Model):
#     _inherit = 'stock.landed.cost'
#
#     audit_period = fields.Boolean(string='Audit Period')