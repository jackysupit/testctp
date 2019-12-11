# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EmployeeEmergencyContact(models.Model):
    _name = 'berdikari.hr.employee.emergency.contact'
    _description = 'Berdikari Employee Emergency Contact'

    employee_id = fields.Many2one('hr.employee')

    name = fields.Char()
    family_relation = fields.Many2one('berdikari.hr.family.relation', store=True)
    address = fields.Char()
    kecamatan = fields.Char()
    kabupaten = fields.Char()
    home_phone = fields.Char()
    mobile_phone = fields.Char()


