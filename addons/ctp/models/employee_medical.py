# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EmployeeMedical(models.Model):
    _name = 'berdikari.hr.employee.medical'
    _description = 'Berdikari Employee Medical'

    employee_id = fields.Many2one('hr.employee')
    medic = fields.Char(string='Clinic / Hospital')
    address = fields.Char(string='Location')
    mobile_phone = fields.Integer(string='Phone')
    blood_type = fields.Selection([('a','A'),('b','B'),('ab','AB'),('o','O')])
    health_condition = fields.Char()
    allergy = fields.Char()
    medicine = fields.Char()
    remarks = fields.Text()