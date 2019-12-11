# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AttendanceCode(models.Model):
    _name = 'berdikari.hr.attendance.code'
    _description = 'Berdikari Attendance Code'

    code = fields.Char()
    name = fields.Selection(selection=[('work', 'Work'), ('absence', 'Absence'), ('off', 'Off'), ('leave', 'Leave'),
                                       ('permit', 'Permit'), ('sick', 'Sick')])
    remarks = fields.Text()
    active = fields.Boolean(default=True)

    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            record.active = not record.active