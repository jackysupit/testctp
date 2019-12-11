# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EmployeeTraining(models.Model):
    _name = 'berdikari.hr.employee.training'
    _description = 'Berdikari Employee Training'

    employee_id = fields.Many2one('hr.employee')
    category_id = fields.Many2one('berdikari.hr.category.type')
    training_type = fields.Many2one('berdikari.hr.training.type')
    company = fields.Char()
    result = fields.Integer()
    year = fields.Integer()
    remarks = fields.Text()