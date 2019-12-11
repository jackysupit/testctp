# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HRDepartment(models.Model):
    _inherit = 'hr.department'

    #Untuk kebutuhan FMS
    is_allow_input_breeding = fields.Boolean(string="Breeding Input")
    is_allow_input_setter = fields.Boolean(string="Setter Input")
    is_allow_input_hatcher = fields.Boolean(string="Hatcher Input")
