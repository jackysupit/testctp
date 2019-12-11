# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError


class EmployeeEducation(models.Model):
    _name = 'berdikari.hr.employee.education'
    _description = 'Berdikari Employee Education'

    employee_id = fields.Many2one('hr.employee')
    education_level = fields.Many2one('berdikari.hr.education.level', store=True)
    school_name = fields.Char()

    def default_year(self):
        ret = datetime.datetime.now().strftime('%Y')
        return ret

    @api.depends('year_graduate')
    @api.onchange('year_graduate')
    def onchange_year_graduate(self):
        for rec in self:
            allow_char = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            if any(x not in allow_char for x in rec.year_graduate):
                raise ValidationError(_("Invalid Year"))

    year_graduate = fields.Char(default=default_year)

    @api.depends('year_entry')
    @api.onchange('year_entry')
    def onchange_year_entry(self):
        for rec in self:
            allow_char = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            if any(x not in allow_char for x in rec.year_entry):
                raise ValidationError(_("Invalid Year"))
    year_entry = fields.Char(default=default_year)

    faculty = fields.Char()
    study = fields.Char()
    grade_point = fields.Float()
    keep_date = fields.Date()
    keep_qty = fields.Integer()
    release_date = fields.Date()
    release_qty = fields.Integer()
    remarks = fields.Text()