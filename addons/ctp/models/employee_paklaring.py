# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EmployeePaklaring(models.Model):
    _name = 'berdikari.hr.employee.paklaring'
    _description = 'Ini adalah model paklaring'

    def _get_employee_id(self):
        # assigning the related employee of the logged in user
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id

    employee_id = fields.Many2one('hr.employee', string='Employee Name', default=_get_employee_id)

    def compute_today(self):
        import datetime
        for rec in self:
            rec.today_date = datetime.datetime.today()

    created_date = fields.Date()

    @api.model_create_multi
    def create(self, vals_list):
        IrSequence = self.env['ir.sequence']
        name = IrSequence.next_by_code('employee.paklaring')
        vals_list[0]['name'] = name
        rec = super(EmployeePaklaring, self).create(vals_list)
        return rec

    name = fields.Char(string='Number', default=lambda self: self.env['ir.sequence'].next_by_code('employee.paklaring'))

    user_id = fields.Many2one('hr.employee', string='Manager Name')
    user_job_id = fields.Many2one('hr.job')
