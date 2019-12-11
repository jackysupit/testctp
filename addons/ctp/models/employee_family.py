# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EmployeeFamily(models.Model):
    _name = 'berdikari.hr.employee.family'
    _description = 'Berdikari Employee Family'

    employee_id = fields.Many2one('hr.employee')

    family_relation = fields.Many2one('berdikari.hr.family.relation', store=True)
    name = fields.Char()
    birth_place = fields.Char()
    birth_date = fields.Date()
    age = fields.Integer()
    bpjs_kesehatan = fields.Char()
    job = fields.Char()


