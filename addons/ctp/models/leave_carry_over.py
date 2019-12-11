# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date, timedelta


class LeaveCarryOver(models.Model):
    _name = 'berdikari.leave.carry.over'
    _description = 'Berdikari Leave Carry Over'

    employee_id = fields.Many2one('hr.employee')
    leave_to_carry_over_period = fields.Char()
    date_today = fields.Date(default=fields.Date.today)
    leave_type_id = fields.Many2one('hr.leave.type')

    @api.depends('leave_type_id', 'employee_id', 'date_today')
    @api.onchange('leave_type_id', 'employee_id', 'date_today')
    def onchange_leave_type_id(self):
        for rec in self:
            model_allocation = self.env['hr.leave.allocation']
            model_leave = self.env['hr.leave']
            leave_alocation = model_allocation.search(
                [('holiday_status_id', '=', rec.leave_type_id.id), ('employee_id', '=', rec.employee_id.id)],
                limit=1).number_of_days
            if rec.date_today and rec.leave_period_end:
                if rec.date_today > rec.leave_period_end:
                    #hitung sisa cuti (carry_over)
                    leave_use = model_leave.search(
                        [('user_id', '=', rec.employee_id.user_id.id), ('state', '=', 'validate'),
                         ('holiday_status_id', '=', rec.leave_type_id.id),
                         ('date_from', '>=', rec.leave_period_start), ('date_to', '<=', rec.leave_period_end)])
                    leave_used = 0
                    for used in leave_use:
                        leave_used = leave_used + used.number_of_days
                    rec.carry_over = leave_alocation - leave_used

                    #hitung cuti yg diambil setelah masa cuti berakhir (carry_used)
                    carry_over_start = date(rec.date_today.year, 1, 1)
                    leave_carry_use = model_leave.search(
                        [('user_id', '=', rec.employee_id.user_id.id), ('state', '=', 'validate'),
                         ('holiday_status_id', '=', rec.leave_type_id.id),
                         ('date_from', '>=', carry_over_start), ('date_to', '<=', rec.carry_cut_off_date)])
                    leave_carry_used = 0
                    for carry_used in leave_carry_use:
                        leave_carry_used = leave_carry_used + carry_used.number_of_days
                    rec.carry_used = leave_carry_used

                    #hitung cuti yg hangus (carry_cut_off)
                    if rec.date_today >= rec.carry_cut_off_date:
                        rec.carry_cut_off = rec.carry_over - rec.carry_used

                    #hitung sisa leave carry over
                    balance = rec.carry_over - rec.carry_used - rec.carry_cut_off
                    rec.carry_over_balance = balance
                else:
                    rec.carry_over = 0
                    rec.carry_used = 0
                    rec.carry_cut_off = 0
                    rec.carry_over_balance = 0

    leave_period_start = fields.Date(related='leave_type_id.validity_start')
    leave_period_end = fields.Date(related='leave_type_id.validity_stop')
    leave_balance = fields.Float(readonly=True)
    carry_cut_off_date = fields.Date(related='leave_type_id.carry_cut_off_date')
    carry_over = fields.Float()  # sisa cuti tahun lalu
    carry_used = fields.Float()  # cuti yg dipakai ditahun berikutnya s.d carry cut off date
    carry_cut_off = fields.Float()  # cuti yg hangus
    carry_over_balance = fields.Float()  # compute

    def action_refresh(self):
        for rec in self:
            date_today = datetime.today()
            rec.date_today = date_today.date()
            rec.onchange_leave_type_id()
