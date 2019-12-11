# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError


class AttendancePeriod(models.Model):
    _name = 'berdikari.hr.attendance.period'
    _description = 'Berdikari Attendance Period'

    code = fields.Char()
    name = fields.Char()
    type = fields.Selection([('monthly','Monthly'),('weekly','Weekly')])

    def default_year(self):
        ret = datetime.datetime.now().strftime('%Y')
        return ret

    @api.depends('year')
    @api.onchange('year')
    def onchange_year(self):
        for rec in self:
            allow_char = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            if any(x not in allow_char for x in rec.year):
                raise ValidationError(_("Invalid Year"))

    year = fields.Char(required=True, default=default_year)
    remarks = fields.Text()

    attendance_period_detail_ids = fields.One2many('berdikari.hr.attendance.period.line', 'attendance_period_id')


class AttendancePeriodLine(models.Model):
    _name = 'berdikari.hr.attendance.period.line'

    attendance_period_id = fields.Many2one('berdikari.hr.attendance.period')
    sequence = fields.Integer()
    name = fields.Char()
    date_from = fields.Date()
    date_to = fields.Date()