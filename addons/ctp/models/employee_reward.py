# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EmployeeReward(models.Model):
    _name = 'berdikari.hr.employee.reward'
    _description = 'Berdikari Employee Reward'

    employee_id = fields.Many2one('hr.employee')

    reward_name = fields.Char()
    date = fields.Date()
    file_doc = fields.Binary(string='Document', attachment=True)
    file_doc_name = fields.Char(string='Document Name')
    remarks = fields.Text()
