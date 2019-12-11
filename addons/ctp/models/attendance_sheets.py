# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date, timedelta
import calendar
import time


class AttendanceSheets(models.Model):
    _name = 'berdikari.attendance.sheets'
    _description = 'Berdikari Attendance Sheets'

    name = fields.Many2one('hr.employee', string='Employee')
    period_id = fields.Many2one('berdikari.hr.attendance.period', string='Period Name')

    @api.depends('period_id')
    @api.onchange('period_id')
    def onchange_domain_seq(self):
        domain = {}
        period_id = self.period_id.id
        if period_id:
            domain_seq = [('attendance_period_id', '=', period_id)]
            domain['period_seq_id'] = domain_seq
        hasil = {'domain': domain}
        return hasil

    period_seq_id = fields.Many2one('berdikari.hr.attendance.period.line', string='Period Sequence')

    @api.depends('period_seq_id')
    @api.onchange('period_seq_id')
    def onchange_period_seq(self):
        for rec in self:
            period_seq_id = rec.period_seq_id.id
            model_period_line = self.env['berdikari.hr.attendance.period.line']
            if period_seq_id:
                period_line = model_period_line.search([('id', '=', period_seq_id)], limit=1)
                rec.period_start = period_line.date_from
                rec.period_end = period_line.date_to

    period_start = fields.Date()
    period_end = fields.Date()
    remarks = fields.Char()
    attendance_policy = fields.Char()
    no_of_overtimes = fields.Integer()
    total_overtime = fields.Float()
    ot_meal_provided = fields.Integer()
    no_of_absence_days = fields.Integer()
    total_absence_hour = fields.Float()
    no_of_lates = fields.Integer()
    total_late_in = fields.Float()
    no_of_diff_times = fields.Integer()
    total_diff_time_hours = fields.Float()
    no_of_work_days = fields.Integer()
    total_work_hours = fields.Float()
    no_of_leave_days = fields.Integer()
    calendar_id = fields.Many2one('resource.calendar')
    attendance_line_ids = fields.One2many('berdikari.attendance.sheets.line', 'attendance_sheet_id')

    @api.multi
    def action_get_attendance(self):
        for rec in self:
            model_attendance = self.env['hr.attendance']
            model_contract = self.env['hr.contract']
            model_calendar = self.env['resource.calendar']
            model_calendar_detail = self.env['resource.calendar.attendance']
            model_overtime = self.env['berdikari.overtime.request']
            model_leave = self.env['hr.leave']
            domain = []
            if rec.name:
                domain.append(('employee_id', '=', rec.name.id))
            else:
                domain = domain
            if rec.period_start and rec.period_end:
                domain.append(('check_in', '>=', rec.period_start))
                domain.append(('check_in', '<=', rec.period_end))
                domain.append(('check_out', '>=', rec.period_start))
                domain.append(('check_out', '<=', rec.period_end))
            else:
                domain = domain
            search_attendance_ids = model_attendance.search(domain, order="id asc")
            domain_name = []
            if rec.name:
                domain_name.append(('employee_id', '=', rec.name.id))
            else:
                domain_name = domain_name
            domain_name.append(('active', '=', True))
            contract_id = model_contract.search(domain_name, limit=1)
            calendar_id = model_calendar.search([('id', '=', contract_id.resource_calendar_id.id)], limit=1)
            rec.calendar_id = calendar_id
            # calendar_detail_ids = model_calendar_detail.search([('calendar_id', '=', calendar_id.id)])
            domain_overtime = []
            if rec.name:
                domain_overtime.append(('employee_id', '=', rec.name.id))
            else:
                domain_overtime = domain_overtime
            if rec.period_start and rec.period_end:
                domain_overtime.append(('start_date', '>=', rec.period_start))
                domain_overtime.append(('start_date', '<=', rec.period_end))
                domain_overtime.append(('state', '=', 'done'))
            else:
                domain_overtime = domain_overtime
            overtime_ids = model_overtime.search(domain_overtime)
            # cek leave
            domain_leave = []
            if rec.name:
                domain_leave.append(('employee_id', '=', rec.name.id))
            else:
                domain_leave = domain_leave
            if rec.period_start and rec.period_end:
                domain_leave.append(('date_from', '>=', rec.period_start))
                domain_leave.append(('date_from', '<=', rec.period_end))
                domain_leave.append(('date_to', '>=', rec.period_start))
                domain_leave.append(('date_to', '<=', rec.period_end))
            else:
                domain_leave = domain_leave
            domain_leave.append(('state', '=', 'validate'))
            leave_ids = model_leave.search(domain_leave)
            # hitung berapa banyak overtime
            no_of_overtimes = len(overtime_ids)
            total_overtime = 0
            ot_meal_provided = 0
            for one in overtime_ids:
                total_overtime = total_overtime + one.numbers_of_hour
                if one.meal_provided:
                    ot_meal_provided = ot_meal_provided + 1
            rec.no_of_overtimes = no_of_overtimes
            rec.total_overtime = total_overtime
            rec.ot_meal_provided = ot_meal_provided
            hasil = []
            no_of_absence_days = 0
            total_absence_hour = 0
            no_of_lates = 0
            total_late_in = 0
            no_of_diff_times = 0
            total_diff_time_hours = 0
            no_of_work_days = 0
            total_work_hours = 0
            no_of_leave_days = 0
            numbers_of_day = ((rec.period_end - rec.period_start).days) + 1
            for a in list(range(numbers_of_day)):
                if a == 0:
                    new_date = rec.period_start.day
                else:
                    new_date = (rec.period_start.day) + a
                schedule_date = date(rec.period_start.year, rec.period_start.month, new_date)
                dayNumber = calendar.weekday(rec.period_start.year, rec.period_start.month, new_date)
                day = calendar.day_name[dayNumber]
                day_to_sign_in = day + ' Morning'
                day_to_sign_out = day + ' Evening'
                sign_in = model_calendar_detail.search([('calendar_id', '=', calendar_id.id), ('name', '=', day_to_sign_in)])
                sign_in_time = sign_in.hour_from
                sign_out = model_calendar_detail.search([('calendar_id', '=', calendar_id.id), ('name', '=', day_to_sign_out)])
                sign_out_time = sign_out.hour_to
                data = False
                actual_sign_in_time = 0
                actual_sign_out_time = 0
                actual_sign_in = 0
                actual_sign_out = 0
                total_working_hour = 0
                nett_working_hour = 0
                overtime_hour = 0
                attendance_code = False
                diff_time = 0
                transport_allowance = 0
                meal_allowance = 0
                ot_meal_provided = False

                t1 = 0
                t2 = 0
                if search_attendance_ids:
                    for data in search_attendance_ids:
                        sign_in_date = date(data.check_in.year, data.check_in.month, data.check_in.day)
                        if sign_in_date == schedule_date:
                            # actual time to show
                            t1 = t1 + data.check_in.hour + 7
                            actual_sign_in_time = data.check_in.strftime("%M")
                            actual_sign_in_time = str(t1) + '.' + actual_sign_in_time
                            t2 = t2 + data.check_out.hour + 7
                            actual_sign_out_time = data.check_out.strftime("%M")
                            actual_sign_out_time = str(t2) + '.' + actual_sign_out_time
                            # actual time to calculate
                            actual_sign_in = data.check_in.hour + (data.check_in.minute / 60) + (
                                        data.check_in.second / 3600) + 7
                            actual_sign_out = data.check_out.hour + (data.check_out.minute / 60) + (
                                        data.check_out.second / 3600) + 7
                            total_working_hour = actual_sign_out - actual_sign_in
                            if day == 'Friday':
                                nett_working_hour = total_working_hour - 1.5
                            else:
                                nett_working_hour = total_working_hour - 1
                            diff_time = (sign_out_time - sign_in_time) - total_working_hour
                            attendance_code_id = self.env['berdikari.hr.attendance.code'].search(
                                [('name', '=', 'work')], limit=1)
                            attendance_code = attendance_code_id.code
                            overtime_hour = 0

                            # hitung berapa banyak late
                            if (actual_sign_in - sign_in_time) > 0:
                                no_of_lates = no_of_lates + 1
                                total_late_in = total_late_in + (actual_sign_in - sign_in_time)
                                rec.no_of_lates = no_of_lates
                                rec.total_late_in = total_late_in

                            # hitung berapa banyak diff
                            setup = self.env['jekdoo.setup'].get_setup()
                            min_diff = setup.diff_limit
                            if diff_time > 0 and diff_time >= min_diff:
                                no_of_diff_times = no_of_diff_times + 1
                                total_diff_time_hours = total_diff_time_hours + diff_time
                                rec.no_of_diff_times = no_of_diff_times
                                rec.total_diff_time_hours = total_diff_time_hours

                            # hitung meal dan transport bila employee check in
                            if (actual_sign_in <= sign_in_time) and nett_working_hour > 5:
                                transport_allowance = transport_allowance + 1
                                meal_allowance = meal_allowance + 1

                            #hitung working days and working hour
                            no_of_work_days = no_of_work_days + 1
                            total_work_hours = total_work_hours + nett_working_hour
                            rec.no_of_work_days = no_of_work_days
                            rec.total_work_hours = total_work_hours

                            if overtime_ids:
                                for overtime in overtime_ids:
                                    overtime_date = date(overtime.start_date.year, overtime.start_date.month,
                                                         overtime.start_date.day)
                                    if overtime_date == sign_in_date:
                                        overtime_hour = overtime.numbers_of_hour
                                        ot_meal_provided = overtime.meal_provided
                                        break
                            break
                        else:
                            if overtime_ids:
                                for overtime in overtime_ids:
                                    overtime_date = date(overtime.start_date.year, overtime.start_date.month,
                                                         overtime.start_date.day)
                                    if overtime_date == schedule_date:
                                        overtime_hour = overtime.numbers_of_hour
                                        ot_meal_provided = overtime.meal_provided
                                        break
                # hitung leave
                if leave_ids:
                    for leave in leave_ids:
                        leave_date_from = date(leave.date_from.year, leave.date_from.month, leave.date_from.day)
                        leave_date_to = date(leave.date_to.year, leave.date_to.month, leave.date_to.day)
                        if leave_date_from == schedule_date or leave_date_to == schedule_date:
                            holiday_status_id = leave.holiday_status_id
                            attendance_code_id = holiday_status_id.attendance_code_id
                            attendance_code = attendance_code_id.code
                            no_of_leave_days = no_of_leave_days + 1
                            rec.no_of_leave_days = no_of_leave_days
                            break
                # hitung berapa banyak absen
                if dayNumber in [0, 1, 2, 3, 4]:
                    if t1 <= 0 or t2 <=0:
                        if attendance_code == False:
                            attendance_code_id = self.env['berdikari.hr.attendance.code'].search([('name', '=', 'absence')],limit=1)
                            attendance_code = attendance_code_id.code
                            if dayNumber == 4:
                                total_absence_hour = total_absence_hour + (sign_out_time - sign_in_time - 1.5)
                            else:
                                total_absence_hour = total_absence_hour + (sign_out_time - sign_in_time - 1)
                            no_of_absence_days = no_of_absence_days + 1
                            rec.no_of_absence_days = no_of_absence_days
                            rec.total_absence_hour = total_absence_hour

                baru = [0, 0, {
                    'attendance_sheet_id': data.id if data else False,
                    'date': schedule_date,
                    'day': day,
                    'planned_sign_in': sign_in_time,
                    'planned_sign_out': sign_out_time,
                    'actual_sign_in_time': actual_sign_in_time,
                    'actual_sign_out_time': actual_sign_out_time,
                    'actual_sign_in': actual_sign_in,
                    'actual_sign_out': actual_sign_out,
                    'late_in': (actual_sign_in - sign_in_time) if (actual_sign_in - sign_in_time) > 0 else 0,
                    'total_working_hour': total_working_hour,
                    'nett_working_hour': nett_working_hour,
                    'overtime': overtime_hour,
                    'ot_meal_provided': ot_meal_provided,
                    'diff_time': diff_time,
                    'transport_allowance': transport_allowance,
                    'meal_allowance': meal_allowance,
                    'attendance_code': attendance_code,
                    'note': '',
                }]
                hasil.append(baru)
            if hasil:
                for line in rec.attendance_line_ids:
                    line.unlink()
                rec.attendance_line_ids = hasil


class AttendanceSheetsLine(models.Model):
    _name = 'berdikari.attendance.sheets.line'
    _description = 'Berdikari Attendance Sheets Line'

    attendance_sheet_id = fields.Many2one('berdikari.attendance.sheets')
    date = fields.Date()
    day = fields.Char()
    planned_sign_in = fields.Float()
    planned_sign_out = fields.Float()
    actual_sign_in_time = fields.Char()
    actual_sign_out_time = fields.Char()
    actual_sign_in = fields.Float()
    actual_sign_out = fields.Float()
    late_in = fields.Float()
    overtime = fields.Float()
    ot_meal_provided = fields.Boolean()
    total_working_hour = fields.Float()
    nett_working_hour = fields.Float()
    diff_time = fields.Float()
    transport_allowance = fields.Integer()
    meal_allowance = fields.Integer()
    # attendance_code = fields.Many2one('berdikari.hr.attendance.code')
    attendance_code = fields.Char()
    note = fields.Char()
