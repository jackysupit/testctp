# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    description = fields.Text(default=lambda self: str(self._context))
    hr_applicant_id = fields.Many2one('hr.applicant')

    @api.model
    def create(self, vals):
        ret = super(IrAttachment, self).create(vals)
        if ret.res_model == 'hr.applicant' and ret.res_id:
            ret.hr_applicant_id = ret.res_id
        return ret


    hr_applicant_name = fields.Char(related='hr_applicant_id.name', string='Application Name', store=True)
    job_id = fields.Many2one('hr.job', related='hr_applicant_id.job_id', string='Applied Job', store=True)
    stage_id = fields.Many2one('hr.recruitment.stage', related='hr_applicant_id.stage_id', string='Application Stage', store=True)
