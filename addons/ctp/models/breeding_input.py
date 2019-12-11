# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.jekdoo.utils.util import Util

from odoo.exceptions import ValidationError, UserError

from dateutil import relativedelta
from datetime import timedelta, datetime


class BreedingInput(models.Model):
    _name = 'berdikari.breeding.input'
    _description = 'Berdikari Breeding Input'

    name = fields.Char(string='Number', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.breeding.input'))
    date = fields.Date(default=fields.Date.today())

    work_order_id = fields.Many2one('berdikari.work.order')
    operating_unit_id = fields.Many2one('operating.unit', string=" Unit", related='work_order_id.operating_unit_id', store=True)
    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)

    company_id = fields.Many2one('res.company', string='Company', related='work_order_id.company_id', store=True)
    house_id = fields.Many2one('berdikari.chicken.coop', string='House', related='work_order_id.house_id', store=True)
    flock_id = fields.Many2one('berdikari.flock.master', string='Flock', related='work_order_id.flock_id', store=True)

    product_product_id = fields.Many2one('product.product', string='Product Name', related='work_order_id.product_product_id', store=True)
    uom_id = fields.Many2one('uom.uom', string='UOM', related='work_order_id.uom_id', store=True)

    start_date = fields.Date(string='Start Date', related='work_order_id.start_date')

    def compute_setup_phase_pertama_id(self):
        row_setup = self.env['jekdoo.setup'].search([], limit=1, order='id desc')
        if row_setup and row_setup.phase_pertama_id:
            for rec in self:
                rec.setup_phase_pertama_id = row_setup.phase_pertama_id.id

    def compute_setup_phase_production(self):
        row_setup = self.env['jekdoo.setup'].search([], limit=1, order='id desc')
        if row_setup and row_setup.phase_production_id:
            for rec in self:
                rec.setup_phase_production_id = row_setup.phase_production_id.id

    def default_setup_phase_pertama_id(self):
        row_setup = self.env['jekdoo.setup'].search([], limit=1, order='id desc')
        default = False
        if row_setup and row_setup.phase_pertama_id:
            default = row_setup.phase_pertama_id.id
        return default

    def default_setup_phase_production(self):
        row_setup = self.env['jekdoo.setup'].search([], limit=1, order='id desc')
        default = False
        if row_setup and row_setup.phase_production_id:
            default = row_setup.phase_production_id.id
        return default

    setup_phase_pertama_id = fields.Many2one('berdikari.phase', default=default_setup_phase_pertama_id, compute=compute_setup_phase_pertama_id)
    setup_phase_production_id = fields.Many2one('berdikari.phase', default=default_setup_phase_production, compute=compute_setup_phase_production)

    def compute_is_phase_production(self):
        for rec in self:
            rec.is_phase_production = rec.setup_phase_production_id == rec.phase_id
    is_phase_production = fields.Boolean(compute=compute_is_phase_production)

    @api.onchange('received_qty','total_by_product', 'breeding_input_line_product')
    def hitung_total_pe(self):
        self.hitung_total_pe_he()

    @api.onchange('breeding_input_line_death')
    def onchange_breeding_input_line_death(self):
        for rec in self:
            total_dead = 0
            for one in rec.breeding_input_line_death:
                total_dead += one.death_qty
            rec.total_dead = total_dead

    @api.onchange('breeding_input_line_feed')
    def onchange_breeding_input_line_feed(self):
        for rec in self:
            total_feed = 0
            for one in rec.breeding_input_line_feed:
                total_feed += one.qty
            rec.total_feed = total_feed

    @api.onchange('breeding_input_line_product')
    def onchange_breeding_input_line_product(self):
        for rec in self:
            total_byproduct = 0
            total_received_qty = 0
            for one in rec.breeding_input_line_product:
                if one.is_result:
                    total_received_qty += one.qty
                else:
                    total_byproduct += one.qty

            rec.received_qty = total_received_qty
            rec.total_by_product = total_byproduct
            rec.hitung_total_pe_he()

    def hitung_total_pe_he(self):
        for rec in self:
            rec.total_pe = rec.received_qty + rec.total_by_product

            wo = rec.work_order_id
            wo_current_pe_hh = wo.current_pe_hh
            wo_current_he_hh = wo.current_he_hh
            wo_begin_qty_female = wo.begin_qty_female
            total_he = rec.received_qty
            total_pe = rec.total_pe

            x = 0.1 + (1000 / 500)
            x = 2.1 + (1000 / 500)

            new_pe_hh = wo_current_pe_hh
            new_he_hh = wo_current_he_hh
            if wo_begin_qty_female:
                new_pe_hh = wo_current_pe_hh + (total_pe / wo_begin_qty_female)
                new_he_hh = wo_current_he_hh + (total_he / wo_begin_qty_female)

            rec.pe_hh = new_pe_hh / 100
            rec.he_hh = new_he_hh / 100

    @api.onchange('date')
    def onchange_date(self):
        for rec in self:
            flock_id = rec.work_order_id.flock_id
            work_order_id = rec.work_order_id
            start_date = work_order_id.start_date
            last_breeding_id = work_order_id.last_breeding_id
            last_breeding_date = last_breeding_id.date

            #todo sementara di buka 1
            # if last_breeding_id:
            #     rec.date = last_breeding_date + timedelta(days=1)
            # else:
            #     rec.date = start_date

            rec.phase_id = work_order_id.current_phase_id.id
            rec.age = work_order_id.current_age

            date = rec.date

            current_day = 0
            start_date = flock_id.start_date
            if start_date:
                current_day = (date - start_date).days + 1

            date = rec.date
            date_1 = start_date
            if date_1:
                current_age = date - date_1
                current_age = int(current_age.days/7) + (current_age.days % 7 > 0)
                rec.age = current_age #weeks

                last_phase = 0
                next_phase_min = 0
                for one in work_order_id.line_breed_ids:
                    if current_age >= next_phase_min and current_age <= one.std_duration:
                        # ini adalah phase sekarang
                        rec.phase_id = one.phase_id
                    next_phase_min = one.std_duration + 1

            rec.is_phase_production = rec.setup_phase_production_id == rec.phase_id

    @api.depends('work_order_id')
    @api.onchange('work_order_id')
    def onchange_work_order_id(self):
        for rec in self:
            work_order_id = rec.work_order_id
            start_date = work_order_id.start_date
            last_breeding_id = work_order_id.last_breeding_id
            if last_breeding_id:
                last_breeding_date = last_breeding_id.date
                rec.date = last_breeding_date + timedelta(days=1)
            else:
                rec.date = start_date

            rec.phase_id = work_order_id.current_phase_id.id
            rec.age = work_order_id.current_age

            date_1 = start_date
            # date_today = fields.Date.today()
            date_today = rec.date
            if date_1:
                current_age = date_today - date_1
                current_age = int(current_age.days/7) + (current_age.days % 7 > 0)
                rec.age = current_age #weeks

                last_phase = 0
                next_phase_min = 0
                max_duration = 0
                for one in work_order_id.line_breed_ids:
                    if one.std_duration > max_duration:
                        max_duration = one.std_duration

                for one in work_order_id.line_breed_ids:
                    if current_age >= max_duration:
                        rec.phase_id = rec.setup_phase_production_id
                    else:
                        if current_age >= next_phase_min and current_age <= one.std_duration:
                            # ini adalah phase sekarang
                            rec.phase_id = one.phase_id

                            #harus pindah phase dulu secara manual di work order
                            # if work_order_id.current_age.id != rec.phase_id.id:
                            #     raise error
                            # else:
                            #     # ini adalah phase sekarang
                            #     rec.phase_id = one.phase_id

                    next_phase_min = one.std_duration + 1

            rec.is_phase_production = rec.setup_phase_production_id == rec.phase_id

            if work_order_id:
                if not rec.breeding_input_line_death:
                    hasil = []
                    for one in work_order_id.line_breed_ids:
                        if one.phase_id.id == work_order_id.current_phase_id.id:
                            baru = [0, 0, {
                                'breeding_input_id': rec.id,
                                'line_breed_id': one.id,
                                'biologis_used_id': one.biologis_used_id.id,
                                'asset_used_id': one.asset_used_id.id,
                                'asset_id': one.asset_id.id,
                                'begin': one.avail_qty,
                                'death_qty': 0,
                                'ending_qty': one.avail_qty,
                                'uom_id': one.uom_id.id,
                                # 'lot_id': one.lot_id.id,
                                'write_off_id': False,
                            }]

                            print('###################### baru: ', baru)

                            hasil.append(baru)
                    if hasil:
                        rec.breeding_input_line_death = hasil

                if not rec.breeding_input_line_feed:
                    hasil = []
                    for one in work_order_id.line_feed_ids:
                        baru = [0, 0, {
                            'breeding_input_id': rec.id,
                            'product_product_id': one.product_product_id.id,
                            'sex': one.product_product_id.sex,
                            # 'product_template_id': one.product_template_id.id,
                            'qty': one.material_planning_qty_line,
                        }]
                        hasil.append(baru)
                    if hasil:
                        rec.breeding_input_line_feed = hasil

                if rec.is_phase_production:
                    if not rec.breeding_input_line_product:
                        hasil = []
                        for one in work_order_id.line_byproduct_ids:
                            baru = [0, 0, {
                                'breeding_input_id': rec.id,
                                'product_product_id': one.product_product_id.id,
                                'sex': one.product_product_id.sex,
                                # 'product_template_id': one.product_template_id.id,
                                'is_result': one.is_result,
                                'qty': one.daily_target,
                            }]
                            hasil.append(baru)
                        if hasil:
                            rec.breeding_input_line_product = hasil

                if not rec.breeding_input_line_ovk:
                    hasil = []
                    for one in work_order_id.line_ovk_ids:
                        baru = [0, 0, {
                            'breeding_input_id': rec.id,
                            'product_product_id': one.product_product_id.id,
                            # 'product_template_id': one.product_template_id.id,
                            'qty': one.material_planning_qty_line,
                        }]
                        hasil.append(baru)
                    if hasil:
                        rec.breeding_input_line_ovk = hasil

    phase_id = fields.Many2one('berdikari.phase', compute=onchange_work_order_id, store=True)
    age = fields.Integer(string='Age (weeks)', compute=onchange_work_order_id, store=True)

    no_bird_female = fields.Integer()
    no_bird_male = fields.Integer()
    total_pe = fields.Integer()
    total_by_product = fields.Integer(string='Total By Product')
    received_qty = fields.Integer(string='Total HE')
    pe_hh = fields.Float(string='PE/HH')
    he_hh = fields.Float(string='HE/HH')

    total_dead = fields.Integer()
    total_feed = fields.Integer()

    def def_default_breeding_input_line_death(self):
        hasil = []
        work_order_id = self.work_order_id
        if work_order_id:
            for one in work_order_id.line_breed_ids:
                if one.phase_id.id == work_order_id.phase_id:
                    baru = [0, 0, {
                        'breeding_input_id': 'temporary',
                        'line_breed_id': one.id,
                        'asset_id': one.asset_id,
                        'begin': one.planning_qty_line,
                        'death_qty': 0,
                        'ending_qty': one.planning_qty_line,
                        'write_off_id': False,
                    }]
                    hasil.append(baru)
        return hasil

    breeding_input_line_death = fields.One2many('berdikari.breeding.input.line.death', 'breeding_input_id', default=def_default_breeding_input_line_death)
    breeding_input_line_feed = fields.One2many('berdikari.breeding.input.line.feed', 'breeding_input_id')
    breeding_input_line_product = fields.One2many('berdikari.breeding.input.line.product', 'breeding_input_id')
    breeding_input_line_ovk = fields.One2many('berdikari.breeding.input.line.ovk', 'breeding_input_id')

    # fms_hatchery_id = fields.Many2one('berdikari.fms.hatchery')

    # @api.multi
    # def action_hachery(self):
    #     ctx = {
    #         'default_breeding_input_id': self.id,
    #     }
    #     action = Util.jek_open_form(
    #         self, model_name='berdikari.fms.hatchery', id=self.fms_hatchery_id.id, ctx=ctx
    #     )
    #     print('action:::::::::::::::, ', action)
    #     return action

    @api.model
    def create(self, vals):
        # todo sementara di buka 2
        # breeding create
        # date = datetime.strptime(vals.get('date'), "%Y-%m-%d").date()
        # if date > fields.Date.today():
        #     raise ValidationError(_('Tanggal tidak boleh maju'))

        self.hitung_total_male_female(vals)
        rec = super(BreedingInput, self).create(vals)

        #UPDATE WORK.ORDER

        wo = rec.work_order_id

        wo_current_pe_hh = wo.current_pe_hh
        wo_current_he_hh = wo.current_he_hh
        wo_begin_qty_female = wo.begin_qty_female
        total_he = rec.received_qty
        total_pe = rec.total_pe
        new_pe_hh = wo_current_pe_hh
        new_he_hh = wo_current_he_hh

        if wo_begin_qty_female:
            new_pe_hh = wo_current_pe_hh + (total_pe / wo_begin_qty_female)
            new_he_hh = wo_current_he_hh + (total_he / wo_begin_qty_female)

        wo.write({
            'last_breeding_id': rec.id,
            # 'begin_qty_male': wo.begin_qty_male + ,
            # 'begin_qty_female': wo.begin_qty_female + ,
            'total_pe': wo.total_pe + rec.total_pe,
            'total_he': wo.total_he + rec.received_qty,
            'current_pe_hh': new_pe_hh,
            'current_he_hh': new_he_hh,
        })

        rec.update_penyusutan_dan_kematian()

        date_plus_1 = rec.date + timedelta(days=1)
        wo.update_age_daily(date_plus_1)

        rec.update_line_breed()
        rec.do_move_feed_ovk()
        # rec.kurangi_aset_qty()

        if rec.is_phase_production:
        # if rec.phase_id == rec.setup_phase_production_id:
            rec.create_write_off()
            rec.do_move_product()
        else:
            rec.kurangi_qty_asset_death()

        # for one in rec.breeding_input_line_product:
        #     total = 0
        #     if one.is_result:
        #         total += one.qty
        #     # rec.write({'received_qty': total})
        #     rec.received_qty = total

        # rec.do_move_telur_he() #ini udah enggak perlu lagi, karena sudah ada di dalam do_move_feed_ovk()

        #
        # model_hatchery = self.env['berdikari.fms.hatchery']
        # rec_hatchery = model_hatchery.create({
        #     'breeding_input_id': rec.id,
        # })
        #
        # rec.write({
        #     'fms_hatchery_id': rec_hatchery.id,
        # })

        return rec

    # @api.multi
    # def write(self, vals):
    #     result = super(BreedingInput, self).write(vals)
    #
    #     for rec in self:
    #         if(rec.fms_hatchery_id == False):
    #             model_hatchery = self.env['berdikari.fms.hatchery']
    #             rec_hatchery = model_hatchery.create({
    #                 'breeding_input_id': rec.id,
    #             })
    #
    #             rec.write({
    #                 'fms_hatchery_id': rec_hatchery.id,
    #             })
    #
    #     return result


    rec_move_kematian_id = fields.Many2one('account.move')
    rec_move_penyusutan_id = fields.Many2one('account.move')

    def update_penyusutan_dan_kematian(self):
        rec = self
        rec.ensure_one()

        setup = self.env['jekdoo.setup'].get_setup()

        journal_kematian_id = setup.journal_kematian_id
        journal_penyusutan_aset_id = setup.journal_penyusutan_aset_id

        if not journal_kematian_id:
            raise ValidationError(_('Journal Write Off belum di-set di Custom Setup'))

        kematian_debit_account_id = journal_kematian_id.default_debit_account_id
        kematian_credit_account_id = journal_kematian_id.default_credit_account_id

        if not kematian_debit_account_id:
            raise ValidationError(_('Default Debit Account for Jurnal Kematian Aset is not set in Custom Setup'))

        if not kematian_credit_account_id:
            raise ValidationError(_('Default Credit Account for Jurnal Kematian Aset is not set in Custom Setup'))

        # product_product_id = rec.product_product_id
        # write_off_qty = rec.write_off_qty
        # standard_price = product_product_id.standard_price
        # value = write_off_qty * standard_price
        flock_id = rec.flock_id

        total_invoice = 0
        all_invoices = rec.flock_id.purchase_id.invoice_ids
        for one in all_invoices:
            if one.state in ['open', 'paid', 'in_payment']:
                total_invoice += one.amount_total_company_signed

        if not total_invoice:
            raise ValidationError(_('Vendor Bill is yet set for the current Flock'))

        param = (flock_id.start_date.strftime('%Y-%m-%d'), self.flock_id.id)
        logos = """
            SELECT SUM(value)
            FROM stock_move
            WHERE "date" >= %s
            AND flock_id = %s
            AND breeding_type = 'feed'
            """
        Total_Feed = self._cr.execute(logos, param)
        Total_Feed = self._cr.fetchone()[0] or 0.0

        logos = """
            SELECT SUM(value)
            FROM stock_move
            WHERE "date" >= %s
            AND flock_id = %s
            AND breeding_type = 'ovk'
            """
        Total_OVK = self._cr.execute(logos, param)
        Total_OVK = self._cr.fetchone()[0] or 0.0

        param = (flock_id.start_date.strftime('%Y-%m-%d'), self.flock_id.id, journal_penyusutan_aset_id.id)
        logos = """
            SELECT SUM(amount)
            FROM account_move
            WHERE "date" >= %s
            AND flock_id = %s
            AND journal_id = %s
            AND journal_type = 'PENYUSUTAN'
            """
        Total_PENYUSUTAN = self._cr.execute(logos, param)
        Total_PENYUSUTAN = self._cr.fetchone()[0] or 0.0

        asset_ids = self.env['account.asset.asset'].search([('flock_id','=',rec.flock_id.id)])
        if not asset_ids:
            raise ValidationError(_('No Asset detected for this flock: {}'.format(rec.flock_id.display_name)))

        # Total_Feed = 1000
        # Total_OVK = 2000
        Total_nilai = total_invoice + Total_Feed + Total_OVK - Total_PENYUSUTAN
        Qty_sisa_seluruh_aset = 0
        for one in asset_ids:
            Qty_sisa_seluruh_aset += one.qty_end

        if Qty_sisa_seluruh_aset:
            HPP = Total_nilai / Qty_sisa_seluruh_aset
        else:
            HPP = 0

        death_qty = 0
        for one in rec.breeding_input_line_death:
            death_qty += one.death_qty

        value_kematian = round(death_qty * HPP)
        Total_nilai_baru = Total_nilai - value_kematian

        duration = flock_id.duration
        all_day_qty = duration * 7
        date = rec.date

        current_day = 0
        start_date = flock_id.start_date
        if start_date:
            current_day = (date - start_date).days + 1

        prod_week = 0
        for one in rec.work_order_id.line_breed_ids:
            if rec.setup_phase_production_id and one.phase_id.id == rec.setup_phase_production_id.id:
                if one.std_duration:
                    prod_week = one.std_duration
                    break

        if not prod_week:
            raise ValidationError(_('Standard Duration for Production Phase is not set in Work Order Lines.'))

        prod_day_start = 1
        if prod_week:
            prod_day_start = ((prod_week - 1) * 7) + 1

        prod_day_qty = 0
        if current_day and duration:
            # prod_day_qty = (duration * 7) - (current_day - 1)
            prod_day_qty = (duration * 7) - (prod_day_start - 1)

        prod_day_qty_current = 0
        if current_day > prod_day_start:
            prod_day_qty_current = (current_day - prod_day_start) + 1

        prod_day_left = prod_day_qty
        if prod_day_qty:
            prod_day_left = prod_day_qty - (prod_day_qty_current - 0)

        Sisa_hari_menuju_72minggu = prod_day_left

        rec.work_order_id.current_day = current_day
        rec.work_order_id.prod_week = prod_week
        rec.work_order_id.prod_day_start = prod_day_start
        rec.work_order_id.prod_day_qty = prod_day_qty
        rec.work_order_id.prod_day_qty_current = prod_day_qty_current
        rec.work_order_id.prod_day_left = prod_day_left
        rec.work_order_id.Sisa_hari_menuju_72minggu = Sisa_hari_menuju_72minggu

        if not prod_day_left:
            raise ValidationError(_('Date production has stopped.'))

        if not Sisa_hari_menuju_72minggu:
            if rec.flock_id.prod_day_qty_current:
                raise ValidationError(_('Production Day in Flock is not set yet.'))
            else:
                raise ValidationError(_('Data date in Flock is invalid.'))

        value_penyusutan = round(Total_nilai_baru / Sisa_hari_menuju_72minggu)

        # print('######################### duration: ', duration)
        # print('######################### all_day_qty: ', all_day_qty)
        # print('######################### start_date: ', start_date)
        # print('######################### date: ', date)
        # print('######################### current_day: ', current_day)
        # print('######################### prod_week: ', prod_week)
        # print('######################### prod_day_start: ', prod_day_start)
        # print('######################### prod_day_qty: ', prod_day_qty)
        # print('######################### prod_day_qty_current: ', prod_day_qty_current)
        # print('######################### prod_day_left: ', prod_day_left)
        # print('######################### Sisa_hari_menuju_72minggu: ', Sisa_hari_menuju_72minggu)
        #
        # print('############ Total_nilai: ', Total_nilai)
        # print('############ HPP: ', HPP)
        # print('############ value_kematian: ', value_kematian)
        # print('############ Total_nilai_baru: ', Total_nilai_baru)
        # print('############ value_penyusutan: ', value_penyusutan)

        satu = {
            'account_id': journal_kematian_id.id,
            'operating_unit_id': rec.operating_unit_id.id,
            # 'flock_id': rec.flock_id.id,
            # 'currency_id': rec.currency_id.id,
        }

        satu_debit = satu.copy()
        satu_debit['account_id'] = kematian_debit_account_id.id
        satu_debit['debit'] = value_kematian

        satu_credit = satu.copy()
        satu_credit['account_id'] = kematian_credit_account_id.id
        satu_credit['credit'] = value_kematian

        move = self.env['account.move']
        vals_move = {
            'date': rec.date.strftime('%Y-%m-%d'),
            'operating_unit_id': rec.operating_unit_id.id,
            'journal_id': journal_kematian_id.id,
            'flock_id': flock_id.id,
            'journal_type': 'KEMATIAN',
            'line_ids': [(0, 0, satu_debit),(0, 0, satu_credit)],
        }
        rec_move_kematian = move.create(vals_move)
        rec_move_kematian.post()

        if not journal_penyusutan_aset_id:
            raise ValidationError(_('Journal Write Off belum di-set di Custom Setup'))

        penyusutan_debit_account_id = journal_penyusutan_aset_id.default_debit_account_id
        penyusutan_credit_account_id = journal_penyusutan_aset_id.default_credit_account_id

        if not penyusutan_debit_account_id:
            raise ValidationError(_('Default Debit Account for Jurnal Penyusutan Aset is not set in Custom Setup'))

        if not penyusutan_credit_account_id:
            raise ValidationError(_('Default Credit Account for Jurnal Penyusutan Aset is not set in Custom Setup'))

        # product_product_id = rec.product_product_id
        # write_off_qty = rec.write_off_qty
        # standard_price = product_product_id.standard_price
        # value = write_off_qty * standard_price
        #
        # if not standard_price:
        #     raise ValidationError(_('Cost Price is not set for product: {}'.format(product_product_id.display_name)))

        satu = {
            'account_id': journal_penyusutan_aset_id.id,
            'operating_unit_id': rec.operating_unit_id.id,
            # 'flock_id': rec.flock_id.id,
            # 'currency_id': rec.currency_id.id,
        }

        satu_debit = satu.copy()
        satu_debit['account_id'] = penyusutan_debit_account_id.id
        satu_debit['debit'] = value_penyusutan

        satu_credit = satu.copy()
        satu_credit['account_id'] = penyusutan_credit_account_id.id
        satu_credit['credit'] = value_penyusutan

        move = self.env['account.move']
        vals_move = {
            'date': rec.date,
            'operating_unit_id': rec.operating_unit_id.id,
            'journal_id': journal_penyusutan_aset_id.id,
            'flock_id': flock_id.id,
            'journal_type': 'PENYUSUTAN',
            'line_ids': [
                (0, 0, satu_debit),
                (0, 0, satu_credit)
            ],
        }
        # print('########################### rec.is_phase_production: ', rec.is_phase_production)
        if rec.is_phase_production:
            rec_move_penyusutan = move.create(vals_move)
            rec_move_penyusutan.post()

            rec.write({
                'rec_move_kematian_id': rec_move_kematian.id,
                'rec_move_penyusutan_id': rec_move_penyusutan.id,
            })
        else:
            rec.write({
                'rec_move_kematian_id': rec_move_kematian.id,
            })

    def hitung_total_male_female(self, vals_list = {}):
        if vals_list:
            total_male = 0
            total_female = 0
            for one in vals_list.get('breeding_input_line_death'):
                vals = one[2]
                sex = vals.get('sex')
                begin = vals.get('begin')
                death_qty = vals.get('death_qty')
                ending_qty = vals.get('ending_qty')
                if sex == 'female':
                    total_female += ending_qty
                else:
                    total_male += ending_qty

            vals_list['no_bird_female'] = total_female
            vals_list['no_bird_male'] = total_male

    def update_line_breed(self):
        for rec in self:
            for one in rec.breeding_input_line_death:
                one.line_breed_id.death_qty += one.death_qty
                one.line_breed_id.avail_qty = one.ending_qty

    def create_write_off(self):
        model_write_off = self.env['berdikari.asset.write.off']
        for rec in self:
            for one in rec.breeding_input_line_death:
                death_qty = one.death_qty
                if death_qty:
                    # Create Write Off
                    record_bio_use = one.biologis_used_id

                    val_write_off = {
                        'biologis_used_id': record_bio_use.id,
                        'breeding_input_line_death_id': one.id,
                        'date': rec.date.strftime('%Y-%m-%d'),
                        'asset_qty': one.begin,
                        'write_off_qty': death_qty,
                        'aquire_value': one.asset_id.value,
                        'accum_depr_value': one.asset_id.current_depreciation_value,
                        # 'write_off_value': death_qty * (one.asset_id.value - one.asset_id.current_depreciation_value),
                    }
                    record_write_off = model_write_off.create(val_write_off)
                    one.write({'write_off_id': record_write_off.id})

                    asset_used_id = one.asset_used_id
                    asset_used_id.write({
                        'qty': asset_used_id.qty - death_qty
                    })

    def kurangi_qty_asset_death(self):
        model_write_off = self.env['berdikari.asset.write.off']
        for rec in self:
            for one in rec.breeding_input_line_death:
                death_qty = one.death_qty
                if death_qty:
                    # Create Write Off
                    # record_bio_use = one.biologis_used_id
                    #
                    # val_write_off = {
                    #     'biologis_used_id': record_bio_use.id,
                    #     'breeding_input_line_death_id': one.id,
                    #     'date': rec.date.strftime('%Y-%m-%d'),
                    #     'asset_qty': one.begin,
                    #     'write_off_qty': death_qty,
                    #     'aquire_value': one.asset_id.value,
                    #     'accum_depr_value': one.asset_id.current_depreciation_value,
                    #     # 'write_off_value': death_qty * (one.asset_id.value - one.asset_id.current_depreciation_value),
                    # }
                    # record_write_off = model_write_off.create(val_write_off)
                    # one.write({'write_off_id': record_write_off.id})

                    asset_used_id = one.asset_used_id
                    asset_used_id.write({
                        'qty': asset_used_id.qty - death_qty
                    })
    #
    #
    # def kurangi_aset_qty(self):
    #     for rec in self:
    #         for one in rec.breeding_input_line_death:
    #             death_qty = one.death_qty
    #             if death_qty:
    #                 # Create Write Off
    #                 record_bio_use = one.biologis_used_id
    #                 asset_used_id = one.asset_used_id.id
    #                 if asset_used_id:
    #                     model_asset_used = self.env['account.asset.asset.used']
    #                     rec_used = model_asset_used.browse(asset_used_id)
    #
    #                     rec_used.write({
    #                         'qty': rec_used.qty - death_qty
    #                     })

    @api.multi
    def do_move_product(self):
        self.ensure_one()

        #validasi cost feed
        total_feed = 0
        for one in self.breeding_input_line_product:
            if one.qty:
                one.do_move()

    @api.multi
    def do_move_feed_ovk(self):
        self.ensure_one()

        #validasi cost feed
        total_feed = 0
        for one in self.breeding_input_line_feed:
            if one.qty:
                product_template_id = one.product_template_id
                if product_template_id:
                    standard_price = product_template_id.standard_price
                    total_feed = total_feed + (one.qty * standard_price)
                    if not standard_price:
                        #validasi cost feed
                        raise ValidationError(_('Product Cost is not set : {}'.format(product_template_id.display_name)))

                    one.do_move()
                    one.do_masukkan_value_ke_asset()

        #validasi cost ovk
        total_ovk = 0
        for one in self.breeding_input_line_ovk:
            if one.qty:
                product_template_id = one.product_template_id
                if product_template_id:
                    standard_price = product_template_id.standard_price
                    total_ovk = total_ovk + (one.qty * standard_price)

                    if not standard_price:
                        raise ValidationError(_('Product Cost is not set: {}'.format(product_template_id.display_name)))

                    one.do_move()
                    one.do_masukkan_value_ke_asset()


        total_value = total_feed + total_ovk
        total_he = self.received_qty
        value_satuan = 0
        feed_satuan = 0
        ovk_satuan = 0
        if total_he:
            value_satuan = total_value / total_he
            feed_satuan = total_feed / total_he
            ovk_satuan = total_ovk / total_he

        total_doc_hidup = 0
        for one in self.breeding_input_line_death:
            total_doc_hidup = total_doc_hidup + one.ending_qty

        if total_doc_hidup:
            ovk_satuan = total_ovk / total_doc_hidup

        #udah gak perlu ini harusnya, kan udah ada do_move() sendiri masing2 untuk OVK maupun Feed
        # reference_ovk = 'OVK {}'.format(self.name)
        # for line_death_id in self.breeding_input_line_death:
        #     line_death_id.add_valuation(ovk_satuan * line_death_id.ending_qty, reference_ovk)

    @api.multi
    def do_move_telur_he(self):
        self.ensure_one()

        move = self.env['stock.move'].create(self._prepare_move_telur_he())
        move.with_context(is_scrap=False)._action_done()
        # self.write({'move_id': move.id, 'state': 'done'})
        return True

    def _prepare_move_telur_he(self):
        self.ensure_one()

        product_product_id = self.product_product_id
        product_template_id = product_product_id.product_tmpl_id
        standard_price = product_template_id.standard_price

        operating_unit_id = self.operating_unit_id
        company_id = self.company_id

        # product_product_id = self.env['product.product'].search([('product_tmpl_id','=',product_template_id.id)], limit=1)
        # scrap_location_id = self.env['stock.location'].search([('operating_unit_id', '=', operating_unit_id.id), ('company_id', 'in', [self.env.user.company_id.id, False])], limit=1)
        # dest_location_id = self.env['stock.location'].search([('operating_unit_id', '=', operating_unit_id.id), ('company_id', '=', self.company_id.id)], limit=1)
        dest_location_id = self.env['stock.location'].search([('operating_unit_id', '=', operating_unit_id.id),], limit=1)
        source_location_id = self.env.ref('stock.location_production')
        # virtual_location_id = self.env.ref('stock.location_production')
        virtual_location_id = self.env.ref('stock.stock_location_stock')

        lot_id = False
        stock_id = False
        if not dest_location_id:
            stock_ids = self.env['stock.quant'].search([
                ('product_id', '=', product_product_id.id),
                # ('company_id', '=', self.env.user.company_id.id),
            ])

            for one in stock_ids:
                if one.quantity - one.reserved_quantity > 0:
                    stock_id = one
                    break

            if stock_ids:
                if not stock_id:
                    stock_id = stock_ids[0]

            if stock_id:
                dest_location_id = stock_id.location_id
                lot_id = stock_id.lot_id

            if not stock_id:
                raise ValidationError(_('Maaf, stock kosong: {}'.format(product_product_id.display_name)))

            if not dest_location_id:
                dest_location_id = virtual_location_id

        partner_id = self.env.user.partner_id
        qty = self.received_qty



        total_feed = 0
        for one in self.breeding_input_line_feed:
            product_template_id = one.product_template_id
            if product_template_id:
                standard_price = product_template_id.standard_price
                total_feed = total_feed + (one.qty * standard_price)
                if not standard_price:
                    raise ValidationError(_('Product Cost is not Set : {}'.format(product_template_id.display_name)))

        total_ovk = 0
        for one in self.breeding_input_line_ovk:
            product_template_id = one.product_template_id
            if product_template_id:
                standard_price = product_template_id.standard_price
                total_ovk = total_ovk + (one.qty * standard_price)
                if not standard_price:
                    raise ValidationError(_('Product Cost is not Set: {}'.format(product_template_id.display_name)))

        total_value = total_feed + total_ovk
        total_he = self.received_qty
        value_satuan = 0
        feed_satuan = 0
        ovk_satuan = 0
        if total_he:
            value_satuan = total_value / total_he
            feed_satuan = total_feed / total_he
            ovk_satuan = total_ovk / total_he

        # value = total_he * (ovk_satuan + feed_satuan)
        value = total_value

        if not total_value:
            raise ValidationError(_('Feed / OVK tidak boleh kosong, harus diisi.'))

        result = {
            'name': self.display_name,
            'origin': self.display_name,
            'product_id': product_product_id.id,
            'product_uom': self.uom_id.id,

            # 'product_qty': qty, #Jangan update field ini, gak boleh sama Odoo. ini sekarang compute. gantinya product_uom_qty
            'product_uom_qty': qty,
            'price_unit': product_template_id.standard_price,
            'value': value,
            # 'remaining_value': value,
            'location_id': source_location_id.id,
            'scrapped': False,
            'location_dest_id': dest_location_id.id,
            'move_line_ids': [(0, 0, {'product_id': product_product_id.id,
                                           'product_uom_id': product_template_id.uom_id.id,
                                           'qty_done': qty,
                                           'location_id': source_location_id.id,
                                           'location_dest_id': dest_location_id.id,
                                           # 'package_id': self.package_id.id,
                                           'owner_id': partner_id.id if partner_id else False,
                                           'lot_id': lot_id.id if lot_id else False, })],
            'restrict_partner_id': partner_id.id if partner_id else False,
            'picking_id': False
        }
        return result


class LineDeath(models.Model):
    _name = 'berdikari.breeding.input.line.death'
    _description = 'Berdikari Breeding Input Line - Death'
    _rec_name = 'asset_id'

    line_breed_id = fields.Many2one('berdikari.work.order.line.breed')
    asset_used_id = fields.Many2one('account.asset.asset.used', related='line_breed_id.asset_used_id')
    breeding_input_id = fields.Many2one('berdikari.breeding.input')
    biologis_used_id = fields.Many2one('berdikari.asset.biologis.used', related='line_breed_id.biologis_used_id')
    write_off_id = fields.Many2one('berdikari.asset.write.off')

    # death
    asset_id = fields.Many2one('account.asset.asset')

    asset_code = fields.Char(related='asset_id.code')
    asset_type = fields.Many2one('account.asset.category', related='asset_id.category_id')

    product_product_id = fields.Many2one('product.product', readonly=True, store=True, related='asset_id.product_product_id')
    product_template_id = fields.Many2one('product.template', readonly=True, store=True, related='asset_id.product_template_id')
    uom_id = fields.Many2one('uom.uom', related='asset_id.uom_id', store=True)


    sex = fields.Selection([('male','Male'),('female','Female')], related='asset_id.sex')
    begin = fields.Integer()
    death_qty = fields.Integer()
    ending_qty = fields.Integer()

    move_id = fields.Many2one('stock.move', 'Scrap Move', readonly=True)
    lot_id = fields.Many2one('stock.production.lot', string='Lot/ Serial Number', related='asset_id.lot_id', store=True)
    # lot_id = fields.Many2one('stock.production.lot', string='Lot/ Serial Number', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done')], string='Status', default="draft")

    @api.onchange('death_qty')
    def onchange_death_qty(self):
        self.ending_qty = self.begin - self.death_qty

    @api.model
    def create(self, vals):
        rec = super(LineDeath, self).create(vals)
        if rec.death_qty:
            rec.do_move()
        return rec

    @api.multi
    def do_move(self):
        self.ensure_one()

        product_product_id = self.product_product_id
        product_template_id = self.product_template_id

        if not product_template_id:
            raise ValidationError(_('Ini adalah data salah karena Product Template tidak ada.'))

        if not product_template_id.uom_id:
            raise ValidationError(_('UOM it not set for {}'.format(product_template_id.display_name)))

        asset_id = self.asset_id
        breeding_input_id = self.breeding_input_id
        operating_unit_id = breeding_input_id.operating_unit_id

        scrap_location_id = self.env['stock.location'].search(
            [('scrap_location', '=', True),
             # ('company_id', 'in', [self.env.user.company_id.id, False])
             ], limit=1)

        stock_ids = self.env['stock.quant'].search([
            ('product_id', '=', product_product_id.id),
            ('location_id.usage', '=', "internal"),
            ('quantity', '>', 0),
            # ('company_id', '=', self.env.user.company_id.id),
        ])

        location_id = False
        location_id_id = False
        lot_id = False
        uom_id = False
        stock_id = False
        for one in stock_ids:
            if one.quantity - one.reserved_quantity > 0:
                stock_id = one
                break

        if stock_ids:
            if not stock_id:
                stock_id = stock_ids[0]

        if stock_id:
            location_id = stock_id.location_id
            location_id_id = location_id.id
            lot_id = stock_id.lot_id
            uom_id = stock_id.product_id.product_tmpl_id.uom_id

        # if not location_id:
        #     location_id = virtual_location_id
        #     location_id_id = virtual_location_id.id

        source_location = location_id
        dest_location = scrap_location_id


        phase_is_production = self.breeding_input_id.is_phase_production
        if phase_is_production:
            value = self.death_qty * product_template_id.standard_price * -1
        else:
            value = 0

        partner_id = self.env.user.partner_id
        vals = {
            'name': self.display_name,
            'origin': self.breeding_input_id.display_name,
            'product_id': product_product_id.id,
            'product_uom': self.uom_id.id or uom_id.id, #ini karena data lama aja, gak ada uom_id
            'operating_unit_id': operating_unit_id.id,

            # 'product_qty': self.death_qty, #Jangan update field ini, gak boleh sama Odoo. ini sekarang compute. gantinya product_uom_qty
            'product_uom_qty': self.death_qty,
            'price_unit': product_template_id.standard_price,
            # 'value': self.death_qty * product_template_id.standard_price * -1,
            # 'remaining_value': self.death_qty * product_template_id.standard_price * -1,
            'value': value,
            # 'remaining_value': 0,

            'location_id': source_location.id,
            'scrapped': True,
            'location_dest_id': scrap_location_id.id,
            'move_line_ids': [(0, 0, {'product_id': product_product_id.id,
                                      'product_uom_id': product_template_id.uom_id.id or uom_id.id,
                                      'qty_done': self.death_qty,
                                      'location_id': source_location.id,
                                      'location_dest_id': dest_location.id,
                                      # 'package_id': self.package_id.id,
                                      'owner_id': partner_id.id if partner_id else False,
                                      'lot_id': self.lot_id.id, })],
            'restrict_partner_id': partner_id.id if partner_id else False,
            'picking_id': asset_id.picking_id.id
        }

        # print('################## location_id.operating_unit_id: ', asset_id.location_id.operating_unit_id)
        # print('################## location_id.operating_unit_id.name: ', asset_id.location_id.operating_unit_id.name)
        # print('################## scrap_location_id.operating_unit_id: ', scrap_location_id.operating_unit_id)
        # print('################## scrap_location_id.operating_unit_id.name: ', scrap_location_id.operating_unit_id.name)
        # print('################## location_id: ', asset_id.location_id)
        # print('################## location_id.name: ', asset_id.location_id.name)
        # print('################## scrap_location_id: ', scrap_location_id)
        # print('################## scrap_location_id.name: ', scrap_location_id.name)
        # print('################## user.operating_unit_ids: ', self.env.user.operating_unit_ids)
        # print('################## user.name: ', self.env.user.display_name)

        move = self.env['stock.move'].create(vals)
        move.with_context(is_scrap=True)._action_done()
        self.write({'move_id': move.id, 'state': 'done'})
        return True

    @api.multi
    def add_valuation(self, value, reference = ''):
        self.ensure_one()

        product_product_id = self.product_product_id
        product_template_id = self.product_template_id
        asset_id = self.asset_id

        scrap_location_id = self.env['stock.location'].search([('scrap_location', '=', True)
                                                                  # , ('company_id', 'in', [self.env.user.company_id.id, False])
                                                               ], limit=1)

        qty = 1
        partner_id = self.env.user.partner_id
        vals = {
            'reference': reference,
            'name': reference or self.display_name,
            'origin': self.breeding_input_id.display_name,
            'product_id': product_product_id.id,
            'product_uom': self.uom_id.id,

            # 'product_qty': self.death_qty, #Jangan update field ini, gak boleh sama Odoo. ini sekarang compute. gantinya product_uom_qty
            'product_uom_qty': qty,
            'price_unit': product_template_id.standard_price,
            'value': value,
            # 'remaining_value': value,

            'location_id': asset_id.location_id.id,
            'scrapped': True,
            'location_dest_id': scrap_location_id.id,
            'move_line_ids': [(0, 0, {'product_id': product_product_id.id,
                                           'product_uom_id': product_template_id.uom_id.id,
                                           'qty_done': qty,
                                           'location_id': asset_id.location_id.id,
                                           'location_dest_id': scrap_location_id.id,
                                           # 'package_id': self.package_id.id,
                                           'owner_id': partner_id.id if partner_id else False,
                                           'lot_id': self.lot_id.id, })],
            'restrict_partner_id': partner_id.id if partner_id else False,
            'picking_id': asset_id.picking_id.id
        }


        move = self.env['stock.move'].create(vals)
        move.with_context(is_scrap=False)._action_done()
        #
        # print('################# DONE MOVE: ', move.id)
        # print('################# Reference: ', reference)
        # print('################# value: ', value)
        # print('################# vals: ', vals)
        # # self.write({'move_id': move.id, 'state': 'done'})
        return True


# ini tuh default == ngambil dari work.order.line.feed
class LineFeed(models.Model):
    _name = 'berdikari.breeding.input.line.feed'
    _description = 'Berdikari Breeding Input Line - Feed'

    breeding_input_id = fields.Many2one('berdikari.breeding.input')
    # feed
    product_product_id = fields.Many2one('product.product')
    product_template_id = fields.Many2one('product.template', related='product_product_id.product_tmpl_id')
    product_template_code = fields.Char(related='product_template_id.default_code')
    uom_id = fields.Many2one('uom.uom', related='product_template_id.uom_id', store=True)

    @api.onchange('product_product_id')
    def onchange_product_product_id(self):
        for rec in self:
            if rec.product_product_id:
                rec.sex = rec.product_product_id.sex

    sex = fields.Selection([('male','Male'),('female','Female')], string='Sex')
    @api.depends('sex')
    @api.onchange('sex')
    def api_depends_sex(self):
        for rec in self:
            sex = rec.sex
            if sex:
                death_ids = rec.breeding_input_id.breeding_input_line_death
                for one in death_ids:
                    if one.sex == sex:
                        rec.doc_product_id = one.product_product_id
    doc_product_id = fields.Many2one('product.product', 'Product DOC')

    qty = fields.Float(string='Qty')
    price = fields.Float(string='Price', related='product_product_id.standard_price', store=True)

    @api.depends('qty', 'price')
    @api.onchange('qty', 'price')
    def compute_qty_price(self):
        for rec in self:
            rec.value = rec.qty * rec.price
    value = fields.Float(compute=compute_qty_price, store=True)

    #3 field ini di isi waktu do_move()
    move_id = fields.Many2one('stock.move', 'Scrap Move', readonly=True)
    location_id = fields.Many2one('stock.location', string='Location')
    # lot_id = fields.Many2one('stock.production.lot', string='Lot/ Serial Number', related='location_id.lot_id')
    lot_id = fields.Many2one('stock.production.lot', string='Lot/ Serial Number')

    batch_id = fields.Char()
    transaction_id = fields.Char()

    @api.model
    def create(self, vals):
        rec = super(LineFeed, self).create(vals)
        return rec

    @api.multi
    def do_move(self):
        if self.qty:
            move = self.env['stock.move'].create(self._prepare_move_values())
            # print('########################## feed.do_move 1 | move.id: ', move.id)

            move.with_context(is_scrap=True)._action_done()
            self.write({'move_id': move.id, 'state': 'done'})
        return True

    def _prepare_move_values(self):
        self.ensure_one()

        product_product_id = self.product_product_id

        # print('self: ', self)
        # print('product_product_id: ', product_product_id)

        product_template_id = self.product_template_id
        # product_product_id = self.env['product.product'].search([('product_tmpl_id','=',product_template_id.id)], limit=1)
        scrap_location_id = self.env['stock.location'].search([('scrap_location', '=', True)
                                                                  # , ('company_id', 'in', [self.env.user.company_id.id, False])
                                                               ], limit=1)

        stock_ids = self.env['stock.quant'].search([
            ('product_id', '=', product_product_id.id),
            # ('company_id', '=', self.env.user.company_id.id),
        ])

        location_id = False
        lot_id = False
        stock_id = False

        if stock_ids:
            for one in stock_ids:
                if one.quantity - one.reserved_quantity > 0:
                    stock_id = one
                    break

            if not stock_id:
                stock_id = stock_ids[0]

        if stock_id:
            location_id = stock_id.location_id
            lot_id = stock_id.lot_id

        if not stock_id:
            raise ValidationError(_('Maaf. Stock kosong: {}'.format(product_product_id.display_name)))

        partner_id = self.env.user.partner_id
        qty = self.qty

        source_location = location_id
        dest_location = scrap_location_id

        value = qty * product_template_id.standard_price
        result = {
            'name': 'Feed/' + self.breeding_input_id.name,
            'origin': self.breeding_input_id.display_name,
            'product_id': product_product_id.id,
            'product_uom': product_product_id.uom_id.id,

            # 'product_qty': qty, #Jangan update field ini, gak boleh sama Odoo. ini sekarang compute. gantinya product_uom_qty
            'product_uom_qty': qty,
            'price_unit': product_template_id.standard_price,
            'value': value * -1,
            # 'remaining_value': value * -1,
            'flock_id': self.breeding_input_id.flock_id.id,
            'date': self.breeding_input_id.date,
            'breeding_type': 'feed',
            'state': 'done',

            'location_id': source_location.id,
            'scrapped': True,
            'location_dest_id': dest_location.id,
            'move_line_ids': [(0, 0, {'product_id': product_product_id.id,
                                           'product_uom_id': product_template_id.uom_id.id,
                                           'qty_done': qty,
                                           'location_id': source_location.id,
                                           'location_dest_id': dest_location.id,
                                           # 'package_id': self.package_id.id,
                                           'owner_id': partner_id.id if partner_id else False,
                                           'lot_id': lot_id.id if lot_id else False, })],
            'restrict_partner_id': partner_id.id if partner_id else False,
            'picking_id': False
        }

        # sex = product_template_id.sex
        # breeding_input_line_death_ids = self.breeding_input_id.breeding_input_line_death
        # line_death_id = False
        #
        # for one in breeding_input_line_death_ids:
        #     if one.product_template_id.sex == product_template_id.sex:
        #         line_death_id = one
        #
        # if line_death_id:
        #     label = 'Breeding {}: {}'.format(self.breeding_input_id.name, product_template_id.display_name)
        #     line_death_id.add_valuation(value, label)

        self.write({'location_id': location_id.id})
        return result

    @api.multi
    def do_masukkan_value_ke_asset(self):
        if self.qty:
            vals = self._prepare_move_values_masukkan_value_ke_asset()
            move = self.env['stock.move'].create(vals)
            # print('########################## vals: ', vals)
            # print('########################## feed.do_move 2 | move.id: ', move.id)

            # move.with_context(is_scrap=True)._action_done()
            move._action_done()
            self.write({'move_id': move.id, 'state': 'done'})

        return True

    def _prepare_move_values_masukkan_value_ke_asset(self):
        self.ensure_one()

        if not self.sex:
            raise ValidationError(_('Sex for Feed is not set yet.'))

        phase_is_production = self.breeding_input_id.is_phase_production
        if phase_is_production:
            line_byproduct_ids = self.breeding_input_id.work_order_id.line_byproduct_ids
            product_product_id = False
            for one in line_byproduct_ids:
                if one.is_result:
                    product_product_id = one.product_product_id
            if not product_product_id:
                raise ValidationError(_('Breeding Result is not set!'))
        else:
            self.api_depends_sex()
            product_product_id = self.doc_product_id
            if not product_product_id:
                raise ValidationError(_('Breeding Result is not set!!'))


        product_template_id = product_product_id.product_tmpl_id

        my_product_id = self.product_product_id
        my_product_template_id = my_product_id.product_tmpl_id

        scrap_location_id = self.env['stock.location'].search([('scrap_location', '=', True)
                                                                  # , ('company_id', 'in', [self.env.user.company_id.id, False])
                                                               ], limit=1)

        stock_ids = self.env['stock.quant'].search([
            ('product_id', '=', my_product_id.id),
            # ('company_id', '=', self.env.user.company_id.id),
        ])

        location_id = False
        lot_id = False
        stock_id = False

        if stock_ids:
            for one in stock_ids:
                if one.quantity - one.reserved_quantity > 0:
                    stock_id = one
                    break

            if not stock_id:
                stock_id = stock_ids[0]

        if stock_id:
            location_id = stock_id.location_id
            lot_id = stock_id.lot_id

        if not stock_id:
            raise ValidationError(_('Maaf. Stock kosong: {}'.format(product_product_id.display_name)))

        partner_id = self.env.user.partner_id
        qty = self.qty
        # qty = 0 #HARUS 0, karena tidak mengurangi stock, hanya mengurangi value
        # qty = 1 #HARUS 0, karena tidak mengurangi stock, hanya mengurangi value
        qty_to_save = 0

        source_location = location_id
        dest_location = scrap_location_id

        value = qty * my_product_template_id.standard_price
        result = {
            'name': 'Feed/' + self.breeding_input_id.name,
            'origin': self.breeding_input_id.display_name,
            'product_id': product_product_id.id,
            'product_uom': product_product_id.uom_id.id,

            # 'product_qty': qty, #Jangan update field ini, gak boleh sama Odoo. ini sekarang compute. gantinya product_uom_qty
            'product_uom_qty': qty_to_save,
            'price_unit': my_product_template_id.standard_price,
            'value': value,
            # 'remaining_value': value * -1,
            'flock_id': self.breeding_input_id.flock_id.id,
            'date': self.breeding_input_id.date,
            'breeding_type': 'feed2',
            'state': 'done',

            'location_id': source_location.id,
            'scrapped': True,
            'location_dest_id': dest_location.id,
            'move_line_ids': [(0, 0, {'product_id': product_product_id.id,
                                           'product_uom_id': product_template_id.uom_id.id,
                                           'qty_done': qty_to_save,
                                           'location_id': source_location.id,
                                           'location_dest_id': dest_location.id,
                                           # 'package_id': self.package_id.id,
                                           'owner_id': partner_id.id if partner_id else False,
                                           'lot_id': lot_id.id if lot_id else False, })],
            'restrict_partner_id': partner_id.id if partner_id else False,
            'picking_id': False
        }

        # sex = product_template_id.sex
        # breeding_input_line_death_ids = self.breeding_input_id.breeding_input_line_death
        # line_death_id = False
        #
        # for one in breeding_input_line_death_ids:
        #     if one.product_template_id.sex == product_template_id.sex:
        #         line_death_id = one
        #
        # if line_death_id:
        #     label = 'Breeding {}: {}'.format(self.breeding_input_id.name, product_template_id.display_name)
        #     line_death_id.add_valuation(value, label)

        self.write({'location_id': location_id.id})
        return result

# ini tuh default == ngambil dari work.order.line.ovk
class LineOVK(models.Model):
    _name = 'berdikari.breeding.input.line.ovk'
    _description = 'Berdikari Breeding Input Line - Other Material / OVK'

    breeding_input_id = fields.Many2one('berdikari.breeding.input')
    # other material
    product_product_id = fields.Many2one('product.product')
    product_template_id = fields.Many2one('product.template', related='product_product_id.product_tmpl_id')
    product_template_code = fields.Char(related='product_template_id.default_code')
    uom_id = fields.Many2one('uom.uom', related='product_template_id.uom_id', store=True)
    qty = fields.Integer(string='Qty')

    @api.onchange('product_product_id')
    def onchange_product_product_id(self):
        for rec in self:
            if rec.product_product_id:
                rec.sex = rec.product_product_id.sex

    sex = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Sex', required=True)
    @api.depends('sex')
    @api.onchange('sex')
    def api_depends_sex(self):
        for rec in self:
            sex = rec.sex
            if sex:
                death_ids = rec.breeding_input_id.breeding_input_line_death
                for one in death_ids:
                    if one.sex == sex:
                        rec.doc_product_id = one.product_product_id
    doc_product_id = fields.Many2one('product.product', 'Product DOC')

    batch_id = fields.Char()
    transaction_id = fields.Char()

    @api.multi
    def do_move(self):
        move = self.env['stock.move'].create(self._prepare_move_values())

        move.with_context(is_scrap=False)._action_done()
        self.write({'move_id': move.id, 'state': 'done'})
        return True

    def _prepare_move_values(self):
        self.ensure_one()

        product_product_id = self.product_product_id
        product_template_id = self.product_template_id

        # product_product_id = self.env['product.product'].search([('product_tmpl_id','=',product_template_id.id)], limit=1)
        # scrap_location_id = self.env['stock.location'].search([('scrap_location', '=', True), ('company_id', 'in', [self.env.user.company_id.id, False])], limit=1)
        scrap_location_id = self.env['stock.location'].search([('scrap_location', '=', True),], limit=1)

        virtual_location_id = self.env.ref('stock.stock_location_stock')

        stock_ids = self.env['stock.quant'].search([
            ('product_id', '=', product_product_id.id),
            # ('company_id', '=', self.env.user.company_id.id),
        ])

        location_id = False
        location_id_id = False
        lot_id = False
        stock_id = False
        for one in stock_ids:
            if one.quantity - one.reserved_quantity > 0:
                stock_id = one
                break

        if stock_ids:
            if not stock_id:
                stock_id = stock_ids[0]

        if stock_id:
            location_id = stock_id.location_id
            location_id_id = location_id.id
            lot_id = stock_id.lot_id

        if not location_id:
            location_id = virtual_location_id
            location_id_id = virtual_location_id.id

        partner_id = self.env.user.partner_id
        qty = self.qty

        value = qty * product_template_id.standard_price
        value = 0

        source_location = scrap_location_id
        dest_location = location_id

        result = {
            'name': 'OVK/' + self.breeding_input_id.name,
            'origin': self.breeding_input_id.display_name,
            'product_id': product_product_id.id,
            'product_uom': product_product_id.uom_id.id,
            'flock_id': self.breeding_input_id.flock_id.id,
            'date': self.breeding_input_id.date,
            'breeding_type': 'ovk',
            'state': 'done',

            # 'product_qty': qty, #Jangan update field ini, gak boleh sama Odoo. ini sekarang compute. gantinya product_uom_qty
            'product_uom_qty': qty,
            'price_unit': product_template_id.standard_price,
            'value': value,
            # 'remaining_value': value,
            'location_id': source_location.id,
            'scrapped': False,
            'location_dest_id': dest_location.id,
            'move_line_ids': [(0, 0, {'product_id': product_product_id.id,
                                           'product_uom_id': product_template_id.uom_id.id,
                                           'qty_done': qty,
                                           'location_id': source_location.id,
                                           'location_dest_id': dest_location.id,
                                           # 'package_id': self.package_id.id,
                                           'owner_id': partner_id.id if partner_id else False,
                                           'lot_id': lot_id.id if lot_id else False, })],
            'restrict_partner_id': partner_id.id if partner_id else False,
            'picking_id': False
        }
        return result

    @api.multi
    def do_masukkan_value_ke_asset(self):
        if self.qty:
            vals = self._prepare_move_values_masukkan_value_ke_asset()
            move = self.env['stock.move'].create(vals)
            # print('########################## vals: ', vals)
            # print('########################## ovk.do_move 2 | move.id: ', move.id)

            # move.with_context(is_scrap=True)._action_done()
            move._action_done()
            self.write({'move_id': move.id, 'state': 'done'})

        return True

    def _prepare_move_values_masukkan_value_ke_asset(self):
        self.ensure_one()

        if not self.sex:
            raise ValidationError(_('Sex for OVK is not set yet.'))

        phase_is_production = self.breeding_input_id.is_phase_production
        if phase_is_production:
            line_byproduct_ids = self.breeding_input_id.work_order_id.line_byproduct_ids
            product_product_id = False
            for one in line_byproduct_ids:
                if one.is_result:
                    product_product_id = one.product_product_id
            if not product_product_id:
                raise ValidationError(_('Breeding Result is not set.'))
        else:
            self.api_depends_sex()
            product_product_id = self.doc_product_id
            if not product_product_id:
                raise ValidationError(_('Breeding Result is not set..'))

        product_template_id = product_product_id.product_tmpl_id

        my_product_id = self.product_product_id
        my_product_template_id = my_product_id.product_tmpl_id

        scrap_location_id = self.env['stock.location'].search([('scrap_location', '=', True)
                                                               # , ('company_id', 'in', [self.env.user.company_id.id, False])
                                                               ], limit=1)

        stock_ids = self.env['stock.quant'].search([
            ('product_id', '=', my_product_id.id),
            # ('company_id', '=', self.env.user.company_id.id),
        ])

        location_id = False
        lot_id = False
        stock_id = False

        if stock_ids:
            for one in stock_ids:
                if one.quantity - one.reserved_quantity > 0:
                    stock_id = one
                    break

            if not stock_id:
                stock_id = stock_ids[0]

        if stock_id:
            location_id = stock_id.location_id
            lot_id = stock_id.lot_id

        if not stock_id:
            raise ValidationError(_('Maaf. Stock kosong: {}'.format(product_product_id.display_name)))

        partner_id = self.env.user.partner_id
        qty = self.qty
        qty_to_save = 0
        # qty = 0  # HARUS 0, karena tidak mengurangi stock, hanya mengurangi value
        # qty = 1  # HARUS 0, karena tidak mengurangi stock, hanya mengurangi value

        source_location = location_id
        dest_location = scrap_location_id

        value = qty * my_product_template_id.standard_price
        result = {
            'name': 'OVK/' + self.breeding_input_id.name,
            'origin': self.breeding_input_id.display_name,
            'product_id': product_product_id.id,
            'product_uom': product_product_id.uom_id.id,

            # 'product_qty': qty, #Jangan update field ini, gak boleh sama Odoo. ini sekarang compute. gantinya product_uom_qty
            'product_uom_qty': qty_to_save,
            'price_unit': my_product_template_id.standard_price,
            'value': value,
            # 'remaining_value': value * -1,
            'flock_id': self.breeding_input_id.flock_id.id,
            'date': self.breeding_input_id.date,
            'breeding_type': 'ovk2',
            'state': 'done',

            'location_id': source_location.id,
            'scrapped': True,
            'location_dest_id': dest_location.id,
            'move_line_ids': [(0, 0, {'product_id': product_product_id.id,
                                      'product_uom_id': product_template_id.uom_id.id,
                                      'qty_done': qty_to_save,
                                      'location_id': source_location.id,
                                      'location_dest_id': dest_location.id,
                                      # 'package_id': self.package_id.id,
                                      'owner_id': partner_id.id if partner_id else False,
                                      'lot_id': lot_id.id if lot_id else False, })],
            'restrict_partner_id': partner_id.id if partner_id else False,
            'picking_id': False
        }

        # sex = product_template_id.sex
        # breeding_input_line_death_ids = self.breeding_input_id.breeding_input_line_death
        # line_death_id = False
        #
        # for one in breeding_input_line_death_ids:
        #     if one.product_template_id.sex == product_template_id.sex:
        #         line_death_id = one
        #
        # if line_death_id:
        #     label = 'Breeding {}: {}'.format(self.breeding_input_id.name, product_template_id.display_name)
        #     line_death_id.add_valuation(value, label)

        self.write({'location_id': location_id.id})
        return result

# ini tuh default == ngambil dari work.order.line.byproduct
class LineProduct(models.Model):
    _name = 'berdikari.breeding.input.line.product'
    _description = 'Berdikari Breeding Input Line - Product'
    _rec_name = 'product_product_id'

    breeding_input_id = fields.Many2one('berdikari.breeding.input')

    product_product_id = fields.Many2one('product.product')
    product_template_id = fields.Many2one('product.template', related='product_product_id.product_tmpl_id')
    product_template_code = fields.Char(related='product_template_id.default_code')
    uom_id = fields.Many2one('uom.uom', related='product_template_id.uom_id', store=True)

    @api.onchange('product_product_id')
    def onchange_product_product_id(self):
        for rec in self:
            rec.sex = rec.product_product_id.sex


    sex = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Sex')

    qty = fields.Float(string='Qty')
    is_result = fields.Boolean(string='Is Result')

    inv_transfer_id = fields.Char(string='Inv. Transfer ID')

    #3 field ini di isi waktu do_move()
    move_id = fields.Many2one('stock.move', 'Scrap Move', readonly=True)
    location_id = fields.Many2one('stock.location', string='Location')
    # lot_id = fields.Many2one('stock.production.lot', string='Lot/ Serial Number', related='location_id.lot_id')
    # lot_id = fields.Many2one('stock.production.lot', string='Lot/ Serial Number', related='location_id')
    lot_id = fields.Many2one('stock.production.lot', string='Lot/ Serial Number')

    @api.model
    def create(self, vals):
        rec = super(LineProduct, self).create(vals)
        return rec

    @api.multi
    def do_move(self):
        move = self.env['stock.move'].create(self._prepare_move_values())
        move.with_context(is_scrap=True)._action_done()
        self.write({'move_id': move.id, 'state': 'done'})
        return True

    def _prepare_move_values(self):
        self.ensure_one()

        product_product_id = self.product_product_id
        product_template_id = self.product_template_id

        # product_product_id = self.env['product.product'].search([('product_tmpl_id','=',product_template_id.id)], limit=1)
        scrap_location_id = self.env['stock.location'].search([('scrap_location', '=', True)
                                                                  # , ('company_id', 'in', [self.env.user.company_id.id, False])
                                                               ], limit=1)
        virtual_location_id = self.env.ref('stock.stock_location_stock')

        stock_ids = self.env['stock.quant'].search([
            ('product_id', '=', product_product_id.id),
            # ('company_id', '=', self.env.user.company_id.id),
        ])

        location_id = False
        location_id_id = False
        lot_id = False
        stock_id = False
        for one in stock_ids:
            if one.quantity - one.reserved_quantity > 0:
                stock_id = one
                break

        if stock_ids:
            if not stock_id:
                stock_id = stock_ids[0]

        if stock_id:
            location_id = stock_id.location_id
            location_id_id = location_id.id
            lot_id = stock_id.lot_id

        if not location_id:
            location_id = virtual_location_id
            location_id_id = virtual_location_id.id

        partner_id = self.env.user.partner_id
        qty = self.qty


        if self.is_result:
            if not product_template_id.standard_price:
                raise ValidationError(_('Cost Price is not set for {}'.format(product_product_id.display_name)))


            value = qty * product_template_id.standard_price
        else:
            value = 0



        source_location = scrap_location_id
        dest_location = location_id

        result = {
            'name': self.display_name,
            'origin': self.breeding_input_id.display_name,
            'product_id': product_product_id.id,
            'product_uom': self.uom_id.id,

            # 'product_qty': qty, #Jangan update field ini, gak boleh sama Odoo. ini sekarang compute. gantinya product_uom_qty
            'product_uom_qty': qty,
            'price_unit': product_template_id.standard_price,
            'value': value,
            # 'remaining_value': value,
            'location_id': source_location.id,
            'scrapped': False,
            'location_dest_id': dest_location.id,
            'move_line_ids': [(0, 0, {'product_id': product_product_id.id,
                                           'product_uom_id': product_template_id.uom_id.id,
                                           'qty_done': qty,
                                           'location_id': source_location.id,
                                           'location_dest_id': dest_location.id,
                                           # 'package_id': self.package_id.id,
                                           'owner_id': partner_id.id if partner_id else False,
                                           'lot_id': lot_id.id if lot_id else False, })],
            'restrict_partner_id': partner_id.id if partner_id else False,
            'picking_id': False
        }
        return result

