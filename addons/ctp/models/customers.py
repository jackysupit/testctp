# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Customers(models.Model):
    _inherit = 'res.partner'





class CustomersPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'Account Payment'

    company = fields.Many2one('res.company')
    audit_period = fields.Boolean(string='Audit Period')
    nego_rate = fields.Boolean(string='Rate Nego')
    rate = fields.Float(string='Rate')
    farm_id = fields.Many2one('operating.unit', string='Unit')
    flock_id = fields.Many2one('berdikari.flock.master')