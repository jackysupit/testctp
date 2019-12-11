# -*- coding: utf-8 -*-

from odoo import models, fields, api

class VATManagement(models.Model):
    _name = 'vat.management'
    _rec_name = 'number'

    number = fields.Char(string='Number', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.vat.management'))
    date = fields.Date(string='Date')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)
    calculated_vat_account = fields.Char(string='Calculated VAT Account')
    journal_id = fields.Many2one('account.account.type')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    calculated = fields.Boolean(string='Calculated')
    notes = fields.Text(string='Notes')
    # ------filter----
    transaction_period_start = fields.Date(string='Transaction Period Start')
    transaction_period_end = fields.Date(string='Transaction Period End')
    partner_id = fields.Many2one('res.partner')
    filter_journal_id = fields.Many2many('account.journal', string='Account')
    vat_name = fields.Char(string='VAT Name')
    is_credited = fields.Boolean(string='Can Be Credited')
    is_paid = fields.Boolean(string='Paid')
    is_send_withholding_tax_slip = fields.Boolean(string='Sent Tax Slip')
    is_calculated = fields.Boolean(string='Calculated')
    # -------------------
    ammount_total_debit_selected = fields.Float(string='Total Debit')
    ammount_total_credit_selected = fields.Float(string='Total Credit')
    ammount_total_calculated_vat = fields.Float(string='Total Calculated VAT')
    vat_management_detail = fields.One2many('vat.management.line','vat_management_id',string='VAT Management Line')

    account_invoice_ids = fields.Many2many('account.invoice')


    @api.multi
    def action_search_data(self):
        for rec in self:
            model_invoice = rec.env['account.invoice']
            domain = []
            if self.transaction_period_start:
                domain.append(('date_invoice', '>=', self.transaction_period_start))
            else:
                domain = domain
            if self.transaction_period_end:
                domain.append(('date_invoice', '<=', self.transaction_period_end))
            else:
                domain = domain
            if self.partner_id:
                domain.append(('partner_id', '=', self.partner_id.id))
            else:
                domain = domain
            if self.is_credited:
                domain.append(('is_ppn_credited', '=', self.is_credited))
            else:
                domain = domain
            if self.is_paid:
                domain.append(('is_ppn_paid', '=', self.is_paid))
            else:
                domain = domain
            if self.is_send_withholding_tax_slip:
                domain.append(('is_certificate_of_withholding_tax_released', '=', self.is_send_withholding_tax_slip))
            else:
                domain = domain
            if self.is_calculated:
                domain.append(('is_ppn_count', '=', self.is_calculated))
            else:
                domain = domain

            search_invoice_ids = model_invoice.search(domain)
            hasil = []
            total_debit = 0
            total_credit = 0
            if search_invoice_ids:
                for data in search_invoice_ids:
                    account_tax_ids = rec.env['account.move.line'].search([('invoice_id', '=', data.id),('tax_line_id', '!=', False)], limit=1)

                    tax_account_id = account_tax_ids.tax_line_id
                    tax_debit = account_tax_ids.debit
                    tax_credit = account_tax_ids.credit
                    total_line = tax_debit - tax_credit
                    total_debit = total_debit + tax_debit
                    total_credit = total_credit + tax_credit
                    baru = [0, 0, {
                        'invoice_id': data.id,
                        'date': data.date_invoice,
                        'number': data.number,
                        'partner_id': data.partner_id,
                        'trans_type': data.type,
                        'reference': data.reference,
                        'account_tax': tax_account_id,
                        'analytic_account_id': False,
                        'analytic_tag_ids': False,
                        'vat_name': data.tax_line_ids.name,
                        'vat_number': data.efaktur_id.name,
                        'vat_date': rec.date,
                        'debit': tax_debit,                #dari journal, nilai debit utk transaksi tersebut
                        'credit': tax_credit,                #dari journal, nilai credit utk transaksi tersebut
                        'total_line': total_line,            #pengurangan debit - credit
                        'is_credited': data.is_ppn_credited,
                        'is_paid': data.is_ppn_paid,
                        'is_send_withholding_tax_slip': data.is_certificate_of_withholding_tax_released,
                        'is_calculated': data.is_ppn_count,
                        'is_calculated_ref_num': data.vat_number,
                    }]
                    hasil.append(baru)
                if hasil:
                    for line in rec.vat_management_detail:
                        line.unlink()
                    rec.vat_management_detail = hasil
        rec.ammount_total_debit_selected = total_debit
        rec.ammount_total_credit_selected = total_credit

    @api.multi
    def action_calculated_post(self):
        for rec in self:
            model_account_invoice = rec.env['account.invoice']
            data_ids = rec.vat_management_detail
            val = []
            for detail in data_ids:
                inv_id = detail.invoice_id
                vat_number = detail.vat_number
                for invoice in inv_id:
                    inv_data = model_account_invoice.search([('id', '=', invoice.id)], limit=1)
                    inv_data.write({
                        'is_ppn_count': True,
                        'vat_number': detail.vat_number
                    })
            rec.write({'calculated': True})


class VATManagementLine(models.Model):
    _name = 'vat.management.line'
    _description = 'Berikari Vat Management Line'

    vat_management_id = fields.Many2one('vat.management')
    pick = fields.Boolean(string='Pick', store=True)
    invoice_id = fields.Many2one('account.invoice', readonly=True)
    date = fields.Date(string='Date', readonly=True)
    number = fields.Char(string='Transaction On Number', readonly=True)
    partner_id = fields.Many2one('res.partner', readonly=True)
    trans_type = fields.Char(string='Transaction Type', readonly=True)
    reference = fields.Char(string='Reference', readonly=True)
    account_tax = fields.Many2one('account.tax', string='Account', readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags', readonly=True)
    vat_name = fields.Char(string='VAT Name', readonly=True)
    vat_number = fields.Char(string='VAT Number', readonly=True)
    vat_date = fields.Date(string='VAT Date', readonly=True)
    debit = fields.Float(sting='Debit', readonly=True)
    credit = fields.Float(string='Credit', readonly=True)
    total_line = fields.Float(string='Total Line', readonly=True)
    is_credited = fields.Boolean(string='Can Be Credit', readonly=True)
    is_paid = fields.Boolean(string='Paid', readonly=True)
    is_send_withholding_tax_slip = fields.Boolean(string='Sent Tax Slip', readonly=True)
    is_calculated = fields.Boolean(string='Calculated', readonly=True)
    is_calculated_ref_num = fields.Char(string='Calculated Ref. Number', readonly=True)