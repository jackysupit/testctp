# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EmployeeAppraisal(models.Model):
    _name = 'berdikari.hr.employee.appraisal'
    _description = 'Berdikari Employee Appraisal'

    employee_id = fields.Many2one('hr.employee')
    appraisal_name = fields.Char()
    competency_id = fields.Many2one('berdikari.hr.competency', store=True)
    date = fields.Date()
    score = fields.Float(string='Score (Number)')
    grade = fields.Char()
    weight = fields.Char()
    final_score = fields.Float()
    appraisal_doc = fields.Binary(attachment=True)
    appraisal_doc_name = fields.Char()
    remarks = fields.Text()