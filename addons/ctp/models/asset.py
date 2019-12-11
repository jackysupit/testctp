# -*- coding: utf-8 -*-
import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, tools, _
from odoo.tools import float_compare, float_is_zero
from odoo.addons.jekdoo.utils.util import Util


class Asset(models.Model):
    _inherit = 'account.asset.asset'
    _description = 'Inherit Account Asset Asset'

    method = fields.Selection([('linear', 'Straighline'), ('degressive', 'Degressive'), ('double_declining', 'Double Declining')], string='Computation Method',
                              required=True, readonly=True, states={'draft': [('readonly', False)]}, default='linear',
                              help="Choose the method to use to compute the amount of depreciation lines.\n  * Linear: Calculated on basis of: Gross Value / Number of Depreciations\n"
                                   "  * Degressive: Calculated on basis of: Residual Value * Degressive Factor")
    # method = fields.Selection(selection_add=[('double_declining', 'Double Declining')])
    # double_declining = fields.Boolean(string='Double Declining')

    one_value = fields.Float(string='Value Satuan')
    one_salvage = fields.Float(string='Salvage Satuan')
    one_residual = fields.Float(string='Residual Satuan')
    qty_start = fields.Integer(string='Begin QTY')

    def compute_used_qty(self):
        for rec in self:
            used_ids = rec.used_ids
            used_qty = 0
            if used_ids:
                for one in used_ids:
                    used_qty += one.qty
            rec.used_qty = used_qty
    used_qty = fields.Integer(string='Used QTY', compute=compute_used_qty)

    def compute_off_qty(self):
        for rec in self:
            used_ids = rec.used_ids
            off_qty = 0
            if used_ids:
                for one in used_ids:
                    off_qty += one.off_qty
            rec.off_qty = off_qty
    off_qty = fields.Integer(string='OFF QTY', compute=compute_off_qty)

    @api.depends('used_ids')
    @api.onchange('used_ids')
    def compute_avail_qty(self):
        for rec in self:
            rec.avail_qty = rec.qty_start - rec.used_qty - rec.off_qty
    avail_qty = fields.Integer(string='Unused QTY', compute=compute_avail_qty)

    def compute_end_qty(self):
        for rec in self:
            rec.qty_end = rec.avail_qty + rec.used_qty
    qty_end = fields.Integer(string='End QTY', compute=compute_end_qty)



    flock_id = fields.Many2one('berdikari.flock.master', store=True)
    std_productivity = fields.Many2one('berdikari.standard.productivity', store=True, string='Standard Productivity')
    total_dead = fields.Many2one('berdikari.asset.write.off', readonly=True)
    product_product_id = fields.Many2one('product.product', )
    product_template_id = fields.Many2one('product.template', )
    lot_id = fields.Many2one('stock.production.lot', string='Lot/ Serial Number')

    location_id = fields.Many2one('stock.location')
    picking_id = fields.Many2one('stock.picking', 'Transfer Reference', index=True, readonly=1)

    uom_id = fields.Many2one('uom.uom', store=True, string='UOM')

    purchase_id = fields.Many2one('purchase.order', string='Purchase Order', related='flock_id.purchase_id')
    sex = fields.Selection(selection=[
        ('male', 'Male'),
        ('female', 'Female'),
    ])

    receipt_ids = fields.One2many('account.asset.asset.receipt', 'asset_id')
    used_ids = fields.One2many('account.asset.asset.used', 'asset_id')
    doc_ids = fields.One2many('account.asset.asset.document', 'asset_id')
    maintenance_ids = fields.One2many('account.asset.asset.maintenance', 'asset_id')
    bio_ids = fields.One2many('account.asset.asset.biological', 'asset_id')
    total_qty_house = fields.Integer(string='Total')

    biologis_used_id = fields.Many2one('berdikari.asset.biologis.used')

    is_next_month_depreciation = fields.Boolean(string='15th above will be next month depreciation')
    is_can_reclass = fields.Boolean(string='Can be Reclass')
    legal_status = fields.Selection(selection=[('clear and clean', 'Clear and Clean'), ('clear and unclear', 'Clear and Unclear'),
                                               ('unclear and clean', 'Unclear and Clean'), ('unclear and unclean', 'Unclear and Unclean')])
    status_availability = fields.Selection(selection=[('available', 'Available'), ('not_available', 'Not Available')])

    @api.depends('depreciation_line_ids')
    @api.onchange('depreciation_line_ids')
    def compute_current_depreciation_line_id(self):
        current_day = fields.Date.today()
        for rec in self:
            current_depreciation_id = False
            for one in rec.depreciation_line_ids:
                if current_day >= one.depreciation_date:
                    current_depreciation_id = one.id
            rec.current_depreciation_line_id = current_depreciation_id

    location = fields.Text()

    current_depreciation_line_id = fields.Many2one('account.asset.depreciation.line', compute=compute_current_depreciation_line_id, store=True)
    current_depreciation_amount = fields.Float(related='current_depreciation_line_id.amount')
    current_depreciation_value = fields.Float(related='current_depreciation_line_id.depreciated_value')
    current_depreciation_remaining_value = fields.Float(related='current_depreciation_line_id.remaining_value')

    method_time = fields.Selection([('number', _('Usefull Life (Years)')), ('end', _('Ending Date'))], string='Time Method',
                                   required=True, readonly=True, default='number',
                                   states={'draft': [('readonly', False)]},
                                   help="Choose the method to use to compute the dates and number of entries.\n"
                                        "  * Number of Entries: Fix the number of entries and the time between 2 depreciations.\n"
                                        "  * Ending Date: Choose the time between 2 depreciations and the date the depreciations won't go beyond.")
    useful_life = fields.Float()
    useful_life_unit = fields.Selection(selection=[('years', 'years'), ('months', 'months'), ('weeks', 'weeks'), ('days', 'days')])
    method_period = fields.Integer(string='Depreciate Every',
                                   help="State here the time between 2 depreciations")
    method_period_unit = fields.Selection(selection=[('years', 'years'), ('months', 'months'), ('weeks', 'weeks'), ('days', 'days')])

    @api.depends('useful_life', 'useful_life_unit', 'method_period', 'method_period_unit')
    @api.onchange('useful_life', 'useful_life_unit', 'method_period', 'method_period_unit')
    def compute_depreciation_number(self):
        for rec in self:
            depreciation_number = 0
            depreciation_date = self.date
            total_days = (depreciation_date.year % 4) and 365 or 366
            max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
            if rec.useful_life_unit == 'years':
                if rec.method_period_unit == 'years':
                    depreciation_number = rec.useful_life / rec.method_period
                elif rec.method_period_unit == 'months':
                    if rec.method_period == 12:
                        depreciation_number = rec.useful_life
                    else:
                        depreciation_number = rec.useful_life * (12 / rec.method_period)
                elif rec.method_period_unit == 'weeks':
                    depreciation_number = rec.useful_life * (12 * rec.method_period)
                elif rec.method_period_unit == 'days':
                    depreciation_number = rec.useful_life * (total_days / rec.method_period)
            elif rec.useful_life_unit == 'months':
                if rec.method_period_unit == 'months':
                    depreciation_number = rec.useful_life / rec.method_period
                elif rec.method_period_unit == 'weeks':
                    depreciation_number = rec.useful_life * rec.method_period
                elif rec.method_period_unit == 'days':
                    depreciation_number = (30 * rec.useful_life) / rec.method_period
            elif rec.useful_life_unit == 'weeks':
                if rec.method_period_unit == 'months':
                    depreciation_number = rec.useful_life / (4 * rec.method_period)
                elif rec.method_period_unit == 'weeks':
                    depreciation_number = rec.useful_life / rec.method_period
                elif rec.method_period_unit == 'days':
                    depreciation_number = (7 * rec.useful_life) / rec.method_period
            elif rec.useful_life_unit == 'days':
                if rec.method_period_unit == 'months':
                    depreciation_number = rec.useful_life / (30 * rec.method_period)
                elif rec.method_period_unit == 'weeks':
                    depreciation_number = rec.useful_life / (7 * rec.method_period)
                elif rec.method_period_unit == 'days':
                    depreciation_number = rec.useful_life / rec.method_period
            rec.method_number = depreciation_number
    method_number = fields.Integer(string='Number of Depreciations', readonly=True,
                                   help="The number of depreciations needed to depreciate your asset")


    @api.multi
    def compute_depreciation_board(self):
        self.ensure_one()
        # import ipdb;
        # ipdb.set_trace()
        posted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: x.move_check).sorted(key=lambda l: l.depreciation_date)
        unposted_depreciation_line_ids = self.depreciation_line_ids.filtered(lambda x: not x.move_check)

        # Remove old unposted depreciation lines. We cannot use unlink() with One2many field
        commands = [(2, line_id.id, False) for line_id in unposted_depreciation_line_ids]

        if self.value_residual != 0.0:
            amount_to_depr = residual_amount = self.value_residual

            # if we already have some previous validated entries, starting date is last entry + method period
            if posted_depreciation_line_ids and posted_depreciation_line_ids[-1].depreciation_date:
                last_depreciation_date = fields.Date.from_string(posted_depreciation_line_ids[-1].depreciation_date)
                depreciation_date = last_depreciation_date + relativedelta(months=+self.method_period)
            else:
                # depreciation_date computed from the purchase date
                depreciation_date = self.date
                if self.date_first_depreciation == 'last_day_period':
                    # depreciation_date = the last day of the month
                    depreciation_date = depreciation_date + relativedelta(day=31)
                    # ... or fiscalyear depending the number of period
                    if self.method_period == 12:
                        depreciation_date = depreciation_date + relativedelta(month=self.company_id.fiscalyear_last_month)
                        depreciation_date = depreciation_date + relativedelta(day=self.company_id.fiscalyear_last_day)
                        if depreciation_date < self.date:
                            depreciation_date = depreciation_date + relativedelta(years=1)
                elif self.first_depreciation_manual_date and self.first_depreciation_manual_date != self.date:
                    # depreciation_date set manually from the 'first_depreciation_manual_date' field
                    depreciation_date = self.first_depreciation_manual_date

            total_days = (depreciation_date.year % 4) and 365 or 366
            month_day = depreciation_date.day
            undone_dotation_number = self._compute_board_undone_dotation_nb(depreciation_date, total_days)

            for x in range(len(posted_depreciation_line_ids), undone_dotation_number):
                sequence = x + 1
                amount = self._compute_board_amount(sequence, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date)
                amount = self.currency_id.round(amount)
                if float_is_zero(amount, precision_rounding=self.currency_id.rounding):
                    continue
                residual_amount -= amount
                vals = {
                    'amount': amount,
                    'asset_id': self.id,
                    'sequence': sequence,
                    'name': (self.code or '') + '/' + str(sequence),
                    'remaining_value': residual_amount,
                    'depreciated_value': self.value - (self.salvage_value + residual_amount),
                    'depreciation_date': depreciation_date,
                }
                commands.append((0, False, vals))
                if self.method_period_unit == 'months':
                    depreciation_date = depreciation_date + relativedelta(months=+self.method_period)
                elif self.method_period_unit == 'weeks':
                    depreciation_date = depreciation_date + relativedelta(days=+(self.method_period * 7))
                elif self.method_period_unit == 'days':
                    depreciation_date = depreciation_date + relativedelta(days=+self.method_period)

                if month_day > 28 and self.date_first_depreciation == 'manual':
                    max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                    depreciation_date = depreciation_date.replace(day=min(max_day_in_month, month_day))

                # datetime doesn't take into account that the number of days is not the same for each month
                if not self.prorata and self.method_period % 12 != 0 and self.date_first_depreciation == 'last_day_period':
                    max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
                    depreciation_date = depreciation_date.replace(day=max_day_in_month)

        self.write({'depreciation_line_ids': commands})
        return True

    # def _compute_board_amount(self, sequence, residual_amount, amount_to_depr, undone_dotation_number, posted_depreciation_line_ids, total_days, depreciation_date):
    #     amount = 0
    #     # print('######################## method: ', self.method)
    #     # import ipdb; ipdb.set_trace()
    #     if sequence == undone_dotation_number:
    #         amount = residual_amount
    #     else:
    #         if self.method == 'linear':
    #             amount = amount_to_depr / (undone_dotation_number - len(posted_depreciation_line_ids))
    #             if self.prorata:
    #                 amount = amount_to_depr / self.method_number_new
    #                 if sequence == 1:
    #                     date = self.date
    #                     if self.method_period % 12 != 0:
    #                         month_days = calendar.monthrange(date.year, date.month)[1]
    #                         days = month_days - date.day + 1
    #                         amount = (amount_to_depr / self.method_number_new) / month_days * days
    #                     else:
    #                         days = (self.company_id.compute_fiscalyear_dates(date)['date_to'] - date).days + 1
    #                         amount = (amount_to_depr / self.method_number_new) / total_days * days
    #         elif self.method == 'degressive':
    #             amount = residual_amount * self.method_progress_factor
    #             if self.prorata:
    #                 if sequence == 1:
    #                     date = self.date
    #                     if self.method_period % 12 != 0:
    #                         month_days = calendar.monthrange(date.year, date.month)[1]
    #                         days = month_days - date.day + 1
    #                         amount = (residual_amount * self.method_progress_factor) / month_days * days
    #                     else:
    #                         days = (self.company_id.compute_fiscalyear_dates(date)['date_to'] - date).days + 1
    #                         amount = (residual_amount * self.method_progress_factor) / total_days * days
            # tambahan utk DDM
            # elif self.method == 'double_declining':
            #     amount = residual_amount * 0.5
            #     if self.prorata:
            #         if sequence == 1:
            #             date = self.date
            #             if self.method_period % 12 != 0:
            #                 month_days = calendar.monthrange(date.year, date.month)[1]
            #                 days = month_days - date.day + 1
            #                 amount = (residual_amount * self.method_progress_factor) / month_days * days
            #             else:
            #                 days = (self.company_id.compute_fiscalyear_dates(date)['date_to'] - date).days + 1
            #                 amount = (residual_amount * self.method_progress_factor) / total_days * days
        # return amount

    # def _compute_board_undone_dotation_nb(self, depreciation_date, total_days):
    #     undone_dotation_number = self.method_number_new
    #     if self.method_time == 'end':
    #         end_date = self.method_end
    #         undone_dotation_number = 0
    #         while depreciation_date <= end_date:
    #             depreciation_date = date(depreciation_date.year, depreciation_date.month, depreciation_date.day) + relativedelta(months=+self.method_period)
    #             undone_dotation_number += 1
    #     if self.prorata:
    #         undone_dotation_number += 1
    #     return undone_dotation_number


    @api.multi
    def action_write_off_input(self):
        ctx = {
            'default_asset_id': self.id,
        }

        model_name = 'berdikari.asset.write.off'
        res_id = False
        action = Util.jek_open_form(
            self, model_name=model_name, id=res_id, ctx=ctx
        )
        return action


class AssetReceipt(models.Model):
    _name = 'account.asset.asset.receipt'
    _description = 'Inherit Account Asset Asset / Receipt'

    asset_id = fields.Many2one('account.asset.asset')
    receipt_id = fields.Many2one('stock.move')
    purchase_line_id = fields.Many2one('purchase.order.line')

    qty = fields.Integer(string='QTY')
    date = fields.Date(default=fields.Date.today())


class AssetUsed(models.Model):
    _name = 'account.asset.asset.used'
    _description = 'Inherit Account Asset Asset / Used'

    asset_id = fields.Many2one('account.asset.asset')
    biologis_used_id = fields.Many2one('berdikari.asset.biologis.used')
    work_order_id = fields.Many2one('berdikari.work.order', related='biologis_used_id.work_order_id')
    work_order_line_breed_id = fields.Many2one('berdikari.work.order.line.breed', related='biologis_used_id.work_order_line_breed_id')
    flock_id = fields.Many2one('berdikari.flock.master', related='biologis_used_id.flock_id', store=True)
    house_id = fields.Many2one('berdikari.chicken.coop', related='biologis_used_id.house_id', store=True)

    total_used = fields.Integer(string='Total QTY', related='biologis_used_id.total_used', store=True)
    first_qty = fields.Integer(string='First QTY')
    qty = fields.Integer(string='QTY')

    def compute_off_qty(self):
        for rec in self:
            rec.off_qty = rec.first_qty - rec.qty
    off_qty = fields.Integer(string='OFF QTY', compute=compute_off_qty)

    date = fields.Date(default=fields.Date.today())


    @api.multi
    def action_write_off_input(self):
        ctx = {
            'default_asset_id': self.asset_id.id,
            'default_asset_qty': self.qty,
            'default_aquire_value': self.asset_id.value,
            'default_write_off_value': self.asset_id.value,
            'default_asset_used_id': self.id,
        }

        model_name = 'berdikari.asset.write.off'
        res_id = False
        action = Util.jek_open_form(
            self, model_name=model_name, id=res_id, ctx=ctx
        )
        return action

class AssetType(models.Model):
    _inherit = 'account.asset.category'
    _description = 'Inherit Account Asset Category'

    sex = fields.Selection(selection=[
        ('male', 'Male'),
        ('female', 'Female'),
    ])
    is_capitalize_assets = fields.Boolean(string='Capitalize Assets')
    moving_type = fields.Selection(selection=[('moving assets', 'Moving Assets'), ('non moving assets', 'Not Moving Assets')])
    is_double_declaining_method = fields.Boolean(string='Double Declining Method')
    is_next_month_depreciation = fields.Boolean(string='15th above will be next month depreciation')
    is_house_mandatory = fields.Boolean(string='House is Mandatory in Assets Data')
    is_flock_mandatory = fields.Boolean(string='Flock is Mandatory in Assets Data')
    useful_life = fields.Float()
    useful_life_unit = fields.Selection(
        selection=[('years', 'years'), ('months', 'months'), ('weeks', 'weeks'), ('days', 'days')])
    method_period = fields.Integer(string='Depreciate Every',
                                   help="State here the time between 2 depreciations")
    method_period_unit = fields.Selection(
        selection=[('years', 'years'), ('months', 'months'), ('weeks', 'weeks'), ('days', 'days')])

    @api.depends('useful_life', 'useful_life_unit', 'method_period', 'method_period_unit')
    @api.onchange('useful_life', 'useful_life_unit', 'method_period', 'method_period_unit')
    def compute_depreciation_number(self):
        for rec in self:
            depreciation_number = 0
            depreciation_date = date.today()
            total_days = (depreciation_date.year % 4) and 365 or 366
            max_day_in_month = calendar.monthrange(depreciation_date.year, depreciation_date.month)[1]
            if rec.useful_life_unit == 'years':
                if rec.method_period_unit == 'years':
                    depreciation_number = rec.useful_life / rec.method_period
                elif rec.method_period_unit == 'months':
                    if rec.method_period == 12:
                        depreciation_number = rec.useful_life
                    else:
                        depreciation_number = rec.useful_life * (12 / rec.method_period)
                elif rec.method_period_unit == 'weeks':
                    depreciation_number = rec.useful_life * (12 * rec.method_period)
                elif rec.method_period_unit == 'days':
                    depreciation_number = rec.useful_life * (total_days / rec.method_period)
            elif rec.useful_life_unit == 'months':
                if rec.method_period_unit == 'months':
                    depreciation_number = rec.useful_life / rec.method_period
                elif rec.method_period_unit == 'weeks':
                    depreciation_number = rec.useful_life * rec.method_period
                elif rec.method_period_unit == 'days':
                    depreciation_number = (30 * rec.useful_life) / rec.method_period
            elif rec.useful_life_unit == 'weeks':
                if rec.method_period_unit == 'months':
                    depreciation_number = rec.useful_life / (4 * rec.method_period)
                elif rec.method_period_unit == 'weeks':
                    depreciation_number = rec.useful_life / rec.method_period
                elif rec.method_period_unit == 'days':
                    depreciation_number = (7 * rec.useful_life) / rec.method_period
            elif rec.useful_life_unit == 'days':
                if rec.method_period_unit == 'months':
                    depreciation_number = rec.useful_life / (30 * rec.method_period)
                elif rec.method_period_unit == 'weeks':
                    depreciation_number = rec.useful_life / (7 * rec.method_period)
                elif rec.method_period_unit == 'days':
                    depreciation_number = rec.useful_life / rec.method_period
            rec.method_number = depreciation_number
    method_number = fields.Integer(string='Number of Depreciations', readonly=True,
                                   help="The number of depreciations needed to depreciate your asset")


class AssetDocument(models.Model):
    _name = 'account.asset.asset.document'
    _description = 'inherit Account Asset Asset / Document'

    asset_id = fields.Many2one('account.asset.asset')
    document_name = fields.Char()
    expired_date = fields.Date()
    legal_id = fields.Char(string='Legal ID')
    location = fields.Char()
    attached_doc = fields.Binary(attachment=True)
    attached_doc_name = fields.Char(string='...')
    document_type = fields.Many2one('berdikari.document.type')
    warning_date = fields.Date()


class AssetMaintenance(models.Model):
    _name = 'account.asset.asset.maintenance'
    _description = 'inherit Account Asset Asset / Maintenance'

    asset_id = fields.Many2one('account.asset.asset')
    name = fields.Char(string='Maintenance Name')
    date = fields.Date(string='Maintenance Date')
    vendor = fields.Many2one('res.partner')
    asset_id_currency_id = fields.Many2one('res.currency', string='Currency', related='asset_id.currency_id', store=True)
    nominal = fields.Monetary(currency_field = 'asset_id_currency_id', store=True)
    remarks = fields.Char()


class AssetBiological(models.Model):
    _name = 'account.asset.asset.biological'
    _description = 'inherit Account Asset Asset / Biological Asstes'

    asset_id = fields.Many2one('account.asset.asset')
    house_id = fields.Many2one('berdikari.chicken.coop')
    end_qty = fields.Integer()


class AssetReport(models.Model):
    _inherit = 'asset.asset.report'
    _description = 'Inherit Report Assets'

    legal_status = fields.Selection(
        selection=[('clear and clean', 'Clear and Clean'), ('clear and unclear', 'Clear and Unclear'),
                   ('unclear and clean', 'Unclear and Clean'), ('unclear and unclean', 'Unclear and Unclean')])
    status_availability = fields.Selection(selection=[('available', 'Available'), ('not_available', 'Not Available')])
    status_perpanjangan_pajak = fields.Char()

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self._cr, 'asset_asset_report')
        self._cr.execute("""
                create or replace view asset_asset_report as (
                    select
                    min(dl.id) as id,
                    dl.name as name,
                    dl.depreciation_date as depreciation_date,
                    a.date as date,
                    (CASE WHEN dlmin.id = min(dl.id)
                      THEN a.value
                      ELSE 0
                      END) as gross_value,
                    dl.amount as depreciation_value,
                    dl.amount as installment_value,
                    (CASE WHEN dl.move_check
                      THEN dl.amount
                      ELSE 0
                      END) as posted_value,
                    (CASE WHEN NOT dl.move_check
                      THEN dl.amount
                      ELSE 0
                      END) as unposted_value,
                    dl.asset_id as asset_id,
                    dl.move_check as move_check,
                    a.category_id as asset_category_id,
                    a.partner_id as partner_id,
                    a.state as state,
					a.legal_status as legal_status,
					a.status_availability as status_availability,
					(CASE WHEN (SELECT DATE_PART('day', ad.expired_date::timestamp - NOW()::timestamp) as day_left) < 30 
						THEN 'need to renew' 
						ELSE 'no need to renew' 
						END) as status_perpanjangan_pajak,
                    count(dl.*) as installment_nbr,
                    count(dl.*) as depreciation_nbr,
                    a.company_id as company_id
                from account_asset_depreciation_line dl
                    left join account_asset_asset a on (dl.asset_id=a.id)
                    left join (select min(d.id) as id,ac.id as ac_id from account_asset_depreciation_line as d inner join account_asset_asset as ac ON (ac.id=d.asset_id) group by ac_id) as dlmin on dlmin.ac_id=a.id
                    left join account_asset_asset_document ad on (a.id = ad.asset_id)
                where a.active is true 
                group by
                    dl.amount,dl.asset_id,dl.depreciation_date,dl.name,
                    a.date, dl.move_check, a.state, a.category_id, a.partner_id, a.company_id,
                    a.value, a.id, a.salvage_value, dlmin.id,
                    ad.expired_date, ad.warning_date
            )""")
