# -*- coding: utf-8 -*-

from odoo import tools
from odoo import models, fields, api


class SummaryAttendance(models.Model):
    _name = 'berdikari.summary.attendance.reporting'
    _description = 'Berdikari Summary Attendance Report'
    # _auto = True

    # operating_unit = fields.Many2one('operating.unit')
    # start_period = fields.Date()
    # end_period = fields.Date()
    name = fields.Many2one('hr.employee')
    bas_id = fields.Many2one('berdikari.attendance.sheets')
    user_id = fields.Many2one('res.users')

    department_id = fields.Many2one('hr.department')
    period_id = fields.Many2one('berdikari.hr.attendance.period')
    period_seq_id = fields.Many2one('berdikari.hr.attendance.period.line')
    work_hour = fields.Float()
    nip = fields.Many2one('hr.employee')

    work = fields.Integer()
    off = fields.Integer()
    leave = fields.Integer()
    sick = fields.Integer()
    permit = fields.Integer()
    absence = fields.Integer()
    ot_15 = fields.Integer()
    ot_20_d = fields.Integer()
    ot_20_h = fields.Integer()
    ot_30 = fields.Integer()
    transport_allowance = fields.Integer()
    meal_allowance = fields.Integer()
    ot_meal_allowance = fields.Integer()

    @api.model_cr
    def init(self):
        table_name = 'berdikari_summary_attendance_reporting'
        print('####################### Connected')
        print('####################### table: ', self._table)

        # tools.drop_view_if_exists(self._cr, table_name)

        user = self.env.user

        self._cr.execute("""
                delete from {table_name} where user_id={user_id}
                """.format(table_name=table_name, user_id=user.id))

        self._cr.execute("""
                insert into {table_name} (name, bas_id, user_id, department_id, period_id, period_seq_id, work_hour, 
                        transport_allowance, meal_allowance, work, off, leave, permit, sick, absence, 
                        ot_15, ot_20_d, ot_20_h, ot_30, ot_meal_allowance)
                    select
                        emp.id,
                        bas.id,
                        {user_id},
                        dept.id as department_id, 
                        bas.period_id as period_id,
                        bas.period_seq_id as period_seq_id,
                        cal.hours_per_day as work_hour,
                        count(case when basl.transport_allowance = 1 then basl.* end) as transport_allowance, 
                        count(case when basl.meal_allowance = 1 then basl.* end) as meal_allowance,
                        count(case when basl.attendance_code = 'W' then basl.* end) as work,
                        count(case when basl.attendance_code = 'O' then basl.* end) as off,	
                        count(case when basl.attendance_code = 'L' then basl.* end) as leave,	
                        count(case when basl.attendance_code = 'P' then basl.* end) as permit,
                        count(case when basl.attendance_code = 'S' then basl.* end) as sick,	
                        count(case when basl.attendance_code = 'A' then basl.* end) as absence,
                        bor.ot_15,
                        bor.ot_20_d,
                        bor.ot_20_h, 
                        bor.ot_30,
                        count(case when basl.ot_meal_provided = true then basl.* end) as ot_meal_allowance
                    from hr_employee emp
                    left join hr_department dept on emp.department_id = dept.id
                    left join berdikari_attendance_sheets bas on emp.id = bas.name
                    left join resource_calendar cal on bas.calendar_id = cal.id
                    left join berdikari_attendance_sheets_line basl on bas.id = basl.attendance_sheet_id
                    left join (
                        select employee_id, count(ot_15) ot_15, count(ot_20_d) ot_20_d, count(ot_20_h) ot_20_h, count(ot_30) ot_30
                        from berdikari_overtime_request
                        where state = 'done'
                        group by employee_id
                        ) bor
                        on emp.id = bor.employee_id
                    group by emp.id, dept.id, 
                        bas.id,
                        bas.period_id,
                        bas.period_seq_id,
                        cal.hours_per_day,
                        bor.ot_15, 
                        bor.ot_20_d,
                        bor.ot_20_h,
                        bor.ot_30
                    order by emp.id asc
                """.format(table_name=table_name, user_id=user.id))
