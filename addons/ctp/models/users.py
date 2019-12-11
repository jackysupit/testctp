# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Users(models.Model):
    _inherit = 'res.users'
    _description = 'Inherit Res User'

    employee_id = fields.Many2one('hr.employee', string='Related Employee')
    job_id = fields.Many2one('hr.job', string='Job Position', related="employee_id.job_id")

    @api.depends('default_operating_unit_id')
    @api.onchange('default_operating_unit_id')
    def compute_operating_unit_id(self):
        for rec in self:
            rec.operating_unit_id = rec.default_operating_unit_id
    operating_unit_id = fields.Many2one('operating.unit', string="Default Unit", compute=compute_operating_unit_id)

    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)

    def compute_read_account_invoice_out_ids(self):
        for rec in self:
            ai = self.env['account.invoice'].search([]) #make sure hanya yg keluar aja (PO)
            rec.read_account_invoice_out_ids = ai.ids
    read_account_invoice_out_ids = fields.One2many('account.invoice', compute=compute_read_account_invoice_out_ids)

    def compute_read_account_invoice_in_ids(self):
        for rec in self:
            ai = self.env['account.invoice'].search([('type','=','in_invoice')]) #make sure hanya yg keluar aja (PO)
            rec.read_account_invoice_in_ids = ai.ids
    read_account_invoice_in_ids = fields.One2many('account.invoice', compute=compute_read_account_invoice_in_ids)

    def compute_read_purchase_order_ids(self):
        for rec in self:
            ids = []
            ai = rec.read_account_invoice_in_ids
            origin_str = []
            for one in ai:
                origin_str.append(one.origin)
            if origin_str:
                ids = self.env['purchase.order'].search([('name', 'in', origin_str)]).ids
            rec.read_purchase_order_ids = ids
            rec.read_account_invoice_out_ids = ai.ids
    read_purchase_order_ids = fields.One2many('purchase.order', compute=compute_read_purchase_order_ids)
