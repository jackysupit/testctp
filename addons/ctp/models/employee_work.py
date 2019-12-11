# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EmployeeWork(models.Model):
    _name = 'berdikari.hr.employee.work'
    _description = 'Berdikari Employee Work'

    employee_id = fields.Many2one('hr.employee')

    company_name = fields.Char()
    # operating_unit_id = fields.Many2one('operating.unit', string='Unit',
    #                                     default=lambda self: self.env.user.default_operating_unit_id)
    #
    # def def_compute_unit_id(self):
    #     for rec in self:
    #         rec.unit_id = rec.operating_unit_id
    unit = fields.Char()


    department = fields.Char()
    last_position = fields.Char()
    employee_status = fields.Selection([('probation','Probation'),('tetap','Tetap'),('kontrak','Kontrak'),('quit','Quit')])
    duration = fields.Float()
    file_doc = fields.Binary(string='Document', attachment=True)
    file_doc_name = fields.Char(string='Document Name')
    remarks = fields.Text()
