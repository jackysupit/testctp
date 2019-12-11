# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
import calendar
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class OvertimeRequest(models.Model):
    _name = 'berdikari.overtime.request'
    _inherit = 'mail.thread'
    _description = 'Berdikari Overtime Request'
    # _rec_name = 'employee_id'

    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id, string='Employee Name', readonly=True)

    employee_id = fields.Many2one('hr.employee', string='Employee', related='user_id.employee_id', store=True)
    parent_id = fields.Many2one('hr.employee', string='Manager', related='employee_id.parent_id', store=True)
    user_parent_id = fields.Many2one('res.users', string='Manager', related='parent_id.user_id', store=True)

    director_id = fields.Many2one('hr.employee', string='Director', related='parent_id.parent_id', store=True)
    user_director_id = fields.Many2one('res.users', string='Director', related='director_id.user_id', store=True)

    name = fields.Char(related='employee_id.name')
    company_id = fields.Many2one('res.company', related='user_id.employee_id.company_id')
    department_id = fields.Many2one('hr.department', related='user_id.employee_id.department_id')
    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)
    category_id = fields.Char()
    start_date = fields.Datetime(track_visibility='onchange')
    end_date = fields.Datetime(track_visibility='onchange')

    @api.depends('start_date', 'end_date')
    @api.onchange('start_date', 'end_date')
    def on_change_date(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                start_dt = fields.Datetime.from_string(rec.start_date)
                finish_dt = fields.Datetime.from_string(rec.end_date)
                difference = relativedelta(finish_dt, start_dt)
                hours = difference.days * 24
                hours = hours + difference.hours
                minutes = difference.minutes / 60
                hours = hours + minutes
                seconds = 0
                rec.numbers_of_hour = hours
                dayNumber = calendar.weekday(rec.start_date.year, rec.start_date.month, rec.start_date.day)
                date = datetime.strftime(rec.start_date, DEFAULT_SERVER_DATE_FORMAT)
                rec.day = calendar.day_name[dayNumber]
                rec.date = date

    day = fields.Char(readonly=True)
    date = fields.Date(readonly=True)
    numbers_of_hour = fields.Float(store=True) #compute dari start_hour dan end_hour
    ot_15 = fields.Integer()
    ot_20_d = fields.Integer()
    ot_20_h = fields.Integer()
    ot_30 = fields.Integer()

    @api.depends('numbers_of_hour', 'week_end_overtime')
    @api.onchange('numbers_of_hour', 'week_end_overtime')
    def onchange_numbers_of_hour(self):
        for rec in self:
            model_emp = self.env['hr.employee']
            model_contract = self.env['hr.contract']
            emp_id = model_emp.search([('user_id', '=', rec.user_id.id)], limit=1)
            contract_id = model_contract.search([('employee_id', '=', emp_id.id)], limit=1)
            wage = contract_id.wage
            meal = contract_id.meal
            ot_rate = wage / 173
            ot_time = rec.numbers_of_hour
            ot_second_time = 0
            first_hour = 0
            next_hour = 0
            total_ot = 0
            ot_15 = 0
            ot_20_d = 0
            ot_20_h = 0
            ot_30 = 0

            if not rec.week_end_overtime:
                if ot_time > 1:
                    first_hour = 1 * 1.5 * ot_rate
                    ot_15 = ot_15 + 1
                    ot_second_time = ot_time - 1
                    if ot_second_time > 3:
                        next_hour = 2 * 2 * ot_rate
                        ot_20_d = ot_20_d + 1
                    else:
                        next_hour = ot_second_time * 2 * ot_rate
                        ot_20_d = ot_20_d + 1
                    total_ot = first_hour + next_hour
                elif ot_time < 1:
                    total_ot = ot_time * 1.5 * ot_rate
                    ot_15 = ot_15 + 1
            else:
                if ot_time > 1:
                    first_hour = 1 * 2 * ot_rate
                    ot_20_h = ot_20_h + 1
                    ot_second_time = ot_time - 1
                    if ot_second_time > 6:
                        next_hour = 6 * 3 * ot_rate
                        ot_30 = ot_30 + 1
                    else:
                        next_hour = ot_second_time * 3 * ot_rate
                        ot_30 = ot_30 + 1
                    total_ot = first_hour + next_hour
                elif ot_time < 1:
                    total_ot = ot_time * 2 * ot_rate
                    ot_20_h = ot_20_h + 1
            rec.overtime_pay = total_ot
            rec.ot_15 = ot_15
            rec.ot_20_h = ot_20_h
            rec.ot_20_d = ot_20_d
            rec.ot_30 = ot_30
            if not rec.meal_provided:
                rec.meal = meal

    currency_id = fields.Many2one('res.currency', string='Currency', store=True)
    overtime_pay = fields.Monetary(currency_field='currency_id', store=True, string='Overtime Pay')
    meal = fields.Monetary(currency_field='currency_id', store=True, string='Meal')
    manager_id = fields.Many2one('hr.employee', related='user_id.employee_id.parent_id')
    approved_date = fields.Date(track_visibility='onchange')
    approved_by = fields.Many2one('hr.employee', track_visibility='onchange')
    dept_approved_date = fields.Date(track_visibility='onchange')
    dept_approved_by = fields.Many2one('hr.employee', track_visibility='onchange')
    dept_manager_id = fields.Many2one('hr.employee', related='manager_id.parent_id', string='Dept Manager')
    overtime_multiple_request = fields.Boolean()
    include_in_payrol = fields.Boolean(track_visibility='onchange')
    meal_provided = fields.Boolean(track_visibility='onchange')
    week_end_overtime = fields.Boolean(track_visibility='onchange')
    job = fields.Text(track_visibility='onchange')
    job_purpose = fields.Text()     #week end overtime only
    notes = fields.Text()
    state = fields.Selection(
        [('new', 'New'),
         ('waiting_first_approve', 'Waiting First Approval'),
         ('waiting_department_approval', 'Waiting Department Approval'),
         ('done', 'Done')],
        default='new',
        string='State', track_visibility='onchange')

    def compute_is_hide_confirm(self):
        for rec in self:
            is_hide = True
            if rec.state == 'new' and rec.user_id.id == self.env.user.id:
                is_hide = False
            rec.is_hide_confirm = is_hide
    is_hide_confirm = fields.Boolean(compute=compute_is_hide_confirm, default=True)

    def compute_is_hide_approve_manager(self):
        for rec in self:
            is_hide = True
            if rec.state == 'new' or rec.state == 'waiting_department_approval' and \
                    rec.user_id.id != self.env.user.id or rec.user_parent_id.id != self.env.user.id:
                is_hide = True
            elif rec.state == 'waiting_first_approve' and rec.user_id.id != self.env.user.id:
                is_hide = False
            rec.is_hide_approve_manager = is_hide
    is_hide_approve_manager = fields.Boolean(compute=compute_is_hide_approve_manager, default=True)

    def compute_is_hide_approve_dept_manager(self):
        for rec in self:
            is_hide = True
            if rec.state == 'new' or rec.state == 'waiting_first_approve' and \
                    rec.user_id.id != self.env.user.id or rec.user_director_id.id != self.env.user.id:
                is_hide = True
            elif rec.state == 'waiting_department_approval' and rec.user_id.id != self.env.user.id:
                is_hide = False
            rec.is_hide_approve_dept_manager = is_hide
    is_hide_approve_dept_manager = fields.Boolean(compute=compute_is_hide_approve_dept_manager, default=True)



    def action_confirm_overtime(self):
        self.state = 'waiting_first_approve'

    def action_approve_overtime(self):
        user_id = self.env.user.id
        model_emp = self.env['hr.employee']
        emp_id = model_emp.search([('user_id', '=', user_id)], limit=1)
        self.approved_by = emp_id
        self.approved_date = date.today()
        self.state = 'waiting_department_approval'

    def action_approve_department_overtime(self):
        user_id = self.env.user.id
        model_emp = self.env['hr.employee']
        emp_id = model_emp.search([('user_id', '=', user_id)], limit=1)
        self.dept_approved_by = emp_id
        self.dept_approved_date = date.today()
        self.state = 'done'



