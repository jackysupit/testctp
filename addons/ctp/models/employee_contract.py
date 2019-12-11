# -*- coding: utf-8 -*-

from odoo import models, fields, api

class EmployeeContracts(models.Model):
    _inherit = 'hr.contract'
    _description = 'Inherit HR Contract'

    transport = fields.Monetary(currency_field='currency_id', store=True, string='Daily Transport')
    meal = fields.Monetary(currency_field='currency_id', store=True, string='Daily Meal')
    functional_allowance = fields.Monetary(currency_field='currency_id', store=True)
    house_allowance = fields.Monetary(currency_field='currency_id', store=True)
    overtime_status = fields.Selection([('no overtime', 'No Overtime'), ('overtime', 'Overtime')])
    overtime_type = fields.Selection([('by request', 'By Request'), ('by attendance', 'By Attendance')])
    job_status = fields.Selection(selection=[('pjs', 'PJS'), ('plt', 'PLT'), ('definitive', 'Definitive')])
    contract_type = fields.Many2one('berdikari.hr.contract.type')

