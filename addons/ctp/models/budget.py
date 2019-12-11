# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.jekdoo.utils.util import Util
import logging
_logger = logging.getLogger(__name__)

class Budget(models.Model):
    _inherit = 'crossovered.budget'
    _description = 'Inherit Crossover Budget'

    npwp_id = fields.Char(string='Nomor NPWP')
    is_pkp = fields.Boolean(string='Taxable Company')
    ppn_ammount = fields.Float(string='Besaran PPN')
    pph_ammount = fields.Float(string='Besaran PPH')
    tax_invoice_id = fields.Char(string='Nomor Faktur Pajak')
    confirm_plan = fields.Boolean(string='Disetujui')
    budget_no = fields.Char(string='Nomor Anggaran')
    notes = fields.Text(string='Notes')
    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)


    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)


    @api.multi
    def action_budget_confirm_plan(self):
        self.write({'confirm_plan': True})
        return Util.jek_pop1('Done')

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info('################################################')
        _logger.info('################################################')
        _logger.info('################################################')
        _logger.info('################################################')
        _logger.info(vals_list)
        IrSequence = self.env['ir.sequence']
        budget_no = IrSequence.next_by_code('crossovered.budget')
        vals_list[0]['budget_no'] = budget_no
        rec = super(Budget, self).create(vals_list)

        return rec

    # @api.multi
    # def write(self, vals):
    #     ret = super(Budget, self).write(vals)
    #     hasil_account = {}
    #     hasil = []
    #     for rec in self:
    #         detail = rec.crossovered_budget_line
    #         print('#################### detail: ', len(detail))
    #         for line in detail:
    #             crossovered_budget_id =line.crossovered_budget_id
    #             date_from = line.date_from
    #             date_to = line.date_to
    #             general_budget_id = line.general_budget_id
    #             general_budget_name = general_budget_id.name
    #             for account in general_budget_id.account_ids:
    #                 code = account.code
    #                 name = account.name
    #                 account_detail = [{
    #                     'budget_id': general_budget_id.id,
    #                     'budget_name': general_budget_name,
    #                     'account_detail': [code, name],
    #                 }]
    #             hasil_account.append(account_detail)
    #             print('######################## hasil_account: ', hasil_account)
    #         hasil.append(hasil_account)
    #         print('######################## hasil: ', hasil)

        # return ret



class BudgetLine(models.Model):
    _inherit = 'crossovered.budget.lines'
    _description = 'Inherit Crossover Budget Lines'

    planned_amount = fields.Monetary(
        'RKAP', required=True,
        help="Amount you plan to earn/spend. Record a positive amount if it is a revenue and a negative amount if it is a cost.")
    practical_amount = fields.Monetary(
        compute='_compute_practical_amount', string='Realisasi',
        help="Amount really earned/spent.")
    theoritical_amount = fields.Monetary(
        compute='_compute_theoritical_amount', string='Teoritis',
        help="Amount you are supposed to have earned/spent at this date.")
    percentage = fields.Float(
        compute='_compute_percentage', string='Pencapaian %',
        help="Comparison between practical and theoretical amount. This measure tells you if you are below or over budget.")
    remarks = fields.Text()


    @api.onchange('general_budget_id')
    def onchange_general_budget_id(self):
        for rec in self:
            general_budget_id = rec.general_budget_id
            account_display = ''
            for account in general_budget_id.account_ids:
                code = account.code
                name = account.name
                if account_display != '':
                    account_display = account_display + ', ' + code + '-' + name
                else:
                    account_display = code + '-' + name
            rec.account_display = account_display
    account_display = fields.Char(string='Account')
