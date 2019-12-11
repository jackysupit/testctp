# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EmployeeLeaves(models.Model):
    _inherit = 'hr.leave.type'
    _description = 'Interit HR Leave Type'

    is_carryover = fields.Boolean(string='Carry Over')
    carry_over_limit = fields.Integer()
    carry_cut_off_date = fields.Date()
    limit_days_req_to_leave = fields.Integer(string='Limit Days Request to Leave')
    attendance_code_id = fields.Many2one('berdikari.hr.attendance.code', store=True)
    is_exclude_weekend_and_holiday = fields.Boolean(string='Exclude Weekend/Holiday')
