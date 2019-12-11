# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo.exceptions import ValidationError


class HRSalaryRule(models.Model):
    _inherit = "hr.salary.rule"
    _description = 'Inherit HR Salary Rule'

    account_id = fields.Many2one('account.account')


class HRSalaryRuleCategory(models.Model):
    _inherit = 'hr.salary.rule.category'
    _description = 'Inherit HR Salary Rule Category'

    header = fields.Boolean()
    order = fields.Integer()




