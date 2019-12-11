# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Job(models.Model):
    _inherit = 'hr.job'

    #Untuk kebutuhan FMS
    is_allow_create_wo = fields.Boolean(string="Create Work Order")
    is_allow_confirm_wo = fields.Boolean(string="Confirm Work Order")
    is_allow_approve_wo = fields.Boolean(string="Approve & Decline Work Order")

    is_allow_validasi_setter = fields.Boolean(string="Validasi Setter")
    is_allow_validasi_hatcher = fields.Boolean(string="Validasi Hatcher")

    is_allow_validasi_hatchery = fields.Boolean(string="Validasi Hatchery")
    is_allow_close_flock = fields.Boolean(string="Close Flock")