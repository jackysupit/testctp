# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Employeepunishment(models.Model):
    _name = 'berdikari.hr.employee.punishment'
    _description = 'Berdikari Employee Punishment'

    employee_id = fields.Many2one('hr.employee')

    punishment_name = fields.Char()
    punishment_type = fields.Many2one('berdikari.hr.punishment.type', store=True)
    date = fields.Date()
    file_doc = fields.Binary(string='Document', attachment=True)
    file_doc_name = fields.Char(string='Document Name')
    remarks = fields.Text()
