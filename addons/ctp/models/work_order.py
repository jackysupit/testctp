# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import  ValidationError
from odoo.addons.jekdoo.utils.util import Util

from dateutil import relativedelta

class WorkOrder(models.Model):
    _name = 'berdikari.work.order'
    _description = 'Berdikari Work Order'

    name = fields.Char(string='Number', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.work.order'))
    flock_id = fields.Many2one('berdikari.flock.master', required=1, read_only=1, store=True)
    flock_state = fields.Selection(related='flock_id.state')
    company_id = fields.Many2one('res.company', read_only=1, related='flock_id.company_id', store=True)
    operating_unit_id = fields.Many2one('operating.unit', string=" Unit", related='flock_id.operating_unit_id', store=True)

    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)

    state = fields.Selection([('draft', 'Draft'),('confirmed', 'Confirmed'),('declined', 'Declined'),('approved', 'Approved'),('open', 'Depreceated'),], default='draft')

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

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        if not self.start_date:
            raise ValidationError(_('Start Date tidak boleh kosong.'))
        self.state = 'confirmed'

    @api.multi
    def action_decline(self):
        if self.state != 'confirmed':
            raise ValidationError(_('State harus Confirmed dulu.'))
        self.state = 'declined'

    @api.multi
    def action_approve(self):
        if self.state != 'confirmed':
            raise ValidationError(_('State harus Confirmed dulu.'))
        self.state = 'approved'

    def compute_is_hide_confirm_wo(self):
        for rec in self:
            is_hide = True
            state = rec.state
            if state == 'draft':
                if self.env.user.job_id:
                    job_id = self.env.user.job_id
                    is_hide = not job_id.is_allow_confirm_wo
            rec.is_hide_confirm_wo = is_hide
    # is_allow_confirm_wo = fields.Boolean(compute=compute_is_allow_confirm_wo)
    is_hide_confirm_wo = fields.Boolean(compute=compute_is_hide_confirm_wo)

    def compute_is_hide_approve_wo(self):
        for rec in self:
            is_hide = True
            state = rec.state
            if state == 'confirmed':
                if self.env.user.job_id:
                    job_id = self.env.user.job_id
                    is_hide = not job_id.is_allow_approve_wo
            rec.is_hide_approve_wo = is_hide
    # is_allow_approve_wo = fields.Boolean(compute=compute_is_allow_approve_wo)
    is_hide_approve_wo = fields.Boolean(compute=compute_is_hide_approve_wo)

    def compute_is_hide_confirm_button(self):
        for rec in self:
            is_hide = True
            if rec.is_allow_confirm_wo and rec.state == 'draft':
                is_hide = False
            rec.is_hide_confirm_button = is_hide
    is_hide_confirm_button = fields.Boolean(compute=compute_is_hide_confirm_button)

    def compute_is_hide_approve_button(self):
        for rec in self:
            is_hide = True
            if rec.is_allow_approve_wo and rec.state == 'draft':
                is_hide = False
            rec.is_hide_approve_button = is_hide
    is_hide_approve_button = fields.Boolean(compute=compute_is_hide_approve_button)

    # commit ya
    # def domain_hose(self):
    #     domain = []
    #     flock_id = self.flock_id
    #     if flock_id:
    #         house_ids = []
    #         rec_exists = self.search([('flock_id', '=', flock_id)])
    #         for rec2 in rec_exists:
    #             house_ids.append(rec2.house_id.id)
    #         domain = [('id', 'not in', house_ids)]
    #     return domain
    @api.onchange('flock_id')
    def onchange_domain_house(self):
        domain = {}
        operating_unit_id = self.flock_id.operating_unit_id.id
        if operating_unit_id:
            domain_house = [('operating_unit_id', '=', operating_unit_id)]
            domain['house_id'] = domain_house

        hasil = {'domain': domain}
        # hasil = {
        #     'domain': {
        #         'house_id': [('operating_unit_id', '=', operating_unit_id)],
        #     }
        # }
        return hasil

    def default_domain_house(self):
        domain = []
        operating_unit_id = self.flock_id.operating_unit_id.id
        if operating_unit_id:
            domain.append(('operating_unit_id', '=', operating_unit_id))

        # domain = [('operating_unit_id', '=', operating_unit_id)]
        return domain
    house_id = fields.Many2one('berdikari.chicken.coop', string='House', domain="[('operating_unit_id','=',operating_unit_id)]")

    date = fields.Date(default=fields.Date.today)
    batch_id = fields.Many2one('berdikari.wo.batch')
    production_type = fields.Selection([('Breeding','breeding'),('Hatchery','hatchery')])

    # product_template_id = fields.Many2one('product.template')

    product_product_id = fields.Many2one('product.product',string='Breeding Result')
    planning_qty = fields.Float(string='Breeding Qty')
    uom_id = fields.Many2one('uom.uom',string='Breeding UOM')

    product_product_id_setter = fields.Many2one('product.product',string='Setter Result')
    planning_qty_setter = fields.Float(string='Setter Qty')
    uom_id_setter = fields.Many2one('uom.uom',string='Setter UOM')

    product_product_id_hatcher = fields.Many2one('product.product',string='Hatcher Result')
    planning_qty_hatcher = fields.Float(string='Hatcher Qty')
    uom_id_hatcher = fields.Many2one('uom.uom',string='Hatcher UOM')

    start_date = fields.Date(related='flock_id.start_date')
    duration = fields.Integer(string='Duration (weeks)', related='flock_id.duration')
    end_date = fields.Date(related='flock_id.end_date')
    current_age = fields.Integer(string='Current Age (weeks)', related='flock_id.current_age')
    current_phase_id = fields.Many2one('berdikari.phase', readonly=True, default=default_setup_phase_pertama_id)

    @api.onchange('start_date', 'duration', 'line_breed_ids', 'flock_id')
    @api.depends('start_date', 'duration', 'line_breed_ids', 'flock_id')
    def onchange_start_date(self):
        # date_1 = datetime.datetime.strptime(start_date, "%m/%d/%y")
        date_1 = self.start_date
        durasi = self.duration
        date_3 = fields.Date.today()
        if date_1:
            end_date = date_1 + relativedelta.relativedelta(weeks=+ durasi)
            self.end_date = end_date
            current_age = date_3 - date_1
            current_age = int(current_age.days/7) + (current_age.days % 7 > 0)
            self.current_age = current_age

            last_phase = 0
            next_phase_min = 0
            for one in self.line_breed_ids:
                current_age = self.current_age
                if current_age >= next_phase_min and current_age <= one.std_duration:
                    # ini adalah phase sekarang
                    self.current_phase_id = one.phase_id
                next_phase_min = one.std_duration + 1

    @api.depends('line_breed_ids')
    @api.onchange('line_breed_ids')
    def compute_first_phase_id(self):
        for rec in self:
            if rec.line_breed_ids:
                durasi_paling_kecil = False
                phase_id_paling_kecil = False
                for one in rec.line_breed_ids:
                    if not durasi_paling_kecil:
                        durasi_paling_kecil = one.std_duration
                        phase_id_paling_kecil = one.phase_id.id
                    else:
                        if one.std_duration < durasi_paling_kecil:
                            durasi_paling_kecil = one.std_duration
                            phase_id_paling_kecil = one.phase_id.id

                rec.first_phase_id = phase_id_paling_kecil
    first_phase_id = fields.Many2one('berdikari.phase', readonly=True, compute=compute_first_phase_id, store=True)

    notes = fields.Text()

    line_breed_ids = fields.One2many('berdikari.work.order.line.breed', 'work_order_id', string='Death')
    line_feed_ids = fields.One2many('berdikari.work.order.line.feed', 'work_order_id', string='Feed')
    line_ovk_ids = fields.One2many('berdikari.work.order.line.ovk', 'work_order_id', string='OVK')
    line_byproduct_ids = fields.One2many('berdikari.work.order.line.byproduct', 'work_order_id', string='Breeding Result')
    line_byproduct_ids_setter = fields.One2many('berdikari.work.order.line.byproduct.setter', 'work_order_id', string='Setter Result')
    line_byproduct_ids_hatcher = fields.One2many('berdikari.work.order.line.byproduct.hatcher', 'work_order_id', string='Hatcher Result')
    line_current_product_ids = fields.One2many('berdikari.work.order.line.current.product', 'work_order_id', string='Current Product')

    @api.onchange('line_byproduct_ids')
    def onchange_line_byproduct_ids(self):
        for rec in self:
            for one in rec.line_byproduct_ids:
                if one.is_result:
                    product_product_id = one.product_product_id
                    if product_product_id:
                        rec.product_product_id = product_product_id.id
                        rec.uom_id = one.uom_id
                        rec.planning_qty = rec.duration * 7 * one.daily_target

    @api.onchange('line_byproduct_ids_setter')
    def onchange_line_byproduct_ids_setter(self):
        for rec in self:
            for one in rec.line_byproduct_ids_setter:
                if one.is_result:
                    if one.product_product_id:
                        rec.product_product_id_setter = one.product_product_id
                        rec.uom_id_setter = one.uom_id
                        rec.planning_qty_setter = rec.duration * 7 * one.daily_target

    @api.onchange('line_byproduct_ids_hatcher')
    def onchange_line_byproduct_ids_hatcher(self):
        for rec in self:
            for one in rec.line_byproduct_ids_hatcher:
                if one.is_result:
                    if one.product_product_id:
                        rec.product_product_id_hatcher = one.product_product_id
                        rec.uom_id_hatcher = one.uom_id
                        rec.planning_qty_hatcher = rec.duration * 7 * one.daily_target

    last_breeding_id = fields.Many2one('berdikari.breeding.input', string='Last Breeding', domain="[('work_order_id','=',id)]")

    #matikan, baca note di bawah
    # begin_qty_male = fields.Integer()

    #ini sengaja cuma female only, karena cuma female yang dipakai untuk perhitungan current_pe_hh
    begin_qty_female = fields.Integer()
    total_pe = fields.Integer()
    total_he = fields.Integer()

    current_day = fields.Integer()
    prod_week = fields.Integer()
    prod_day_start = fields.Integer()
    prod_day_qty = fields.Integer()
    prod_day_qty_current = fields.Integer()
    prod_day_left = fields.Integer()
    Sisa_hari_menuju_72minggu = fields.Integer()

    #current_pe_hh = total_pe / begin_qty_female
    current_pe_hh = fields.Float(string='Current PE/HH')
    current_he_hh = fields.Float(string='Current HE/HH')

    @api.onchange('total_pe')
    @api.depends('total_pe')
    def onchange_total_pe(self):
        for rec in self:
            if rec.id and rec.begin_qty_female:
                rec.current_pe_hh = rec.total_pe / rec.begin_qty_female

    breeding_ids = fields.One2many('berdikari.breeding.input', 'work_order_id', string='Breeding')
    def compute_count_breeding(self):
        for rec in self:
            rec.count_breeding = len(rec.breeding_ids)
    count_breeding = fields.Integer(compute=compute_count_breeding)

    def compute_is_bio_use(self):
        phase_pertama_id = False
        row_setup = self.env['jekdoo.setup'].search([], limit=1, order="id desc")
        if row_setup and row_setup.phase_pertama_id:
            phase_pertama_id = row_setup.phase_pertama_id

        if phase_pertama_id:
            for rec in self:
                is_bio_use = True  # default, sudah
                for one in rec.line_breed_ids:
                    # print('##BBBBBBBBBBBBBBBBBBBBB one.phase_id.id: ', one.phase_id.id)
                    # print('##BBBBBBBBBBBBBBBBBBBBB phase_pertama_id: ', phase_pertama_id)
                    # print('##BBBBBBBBBBBBBBBBBBBBB one.biologis_used_id: ', one.biologis_used_id)
                    if one.phase_id.id == phase_pertama_id.id and not one.biologis_used_id:
                        is_bio_use = False
                rec.is_bio_use = is_bio_use

    #validasi semua breeding sudah bio_use -> true = semua breeding sudah bio use | false = jika ada yg masih belum bio use
    is_bio_use = fields.Boolean(compute=compute_is_bio_use)

    hatcher_ids = fields.One2many('berdikari.fms.grading.hatcher', 'work_order_id', string='Hatcher')
    def compute_count_hatcher(self):
        for rec in self:
            rec.count_hatcher = len(rec.hatcher_ids)
    count_hatcher = fields.Integer(compute=compute_count_hatcher)

    setter_ids = fields.One2many('berdikari.fms.grading.setter', 'work_order_id', string='Setter')
    def compute_count_setter(self):
        for rec in self:
            rec.count_setter = len(rec.setter_ids)
    count_setter = fields.Integer(compute=compute_count_setter)

    biologis_used_id = fields.Many2one('berdikari.asset.biologis.used')

    @api.model
    def create(self, vals):
        house_id = vals.get('house_id')
        if not house_id:
            # raise ValidationError(_('{} is required!'.format('Hose')))
            print('Do Nothing, buka aja buat fitur Duplicate!')
        else:
            model_hose = self.env['berdikari.chicken.coop']

            flock_id = vals.get('flock_id')

            rec_exists = self.search([('flock_id','=',flock_id), ('house_id','=',house_id)], limit=1)
            if rec_exists:
                raise ValidationError(_('{} is already exists for this flock: {}'.format('Hose', rec_exists.flock_id.display_name)))

        rec = super(WorkOrder, self).create(vals)
        return rec

    def cek_duplicate_house_id(self, vals):
        self.ensure_one()
        house_id = vals.get('house_id')
        if house_id:
            flock_id = vals.get('flock_id') or self.flock_id.id
            rec_exists = self.search([('flock_id','=',flock_id), ('house_id','=',house_id), ('id', '!=', self.id)], limit=1)
            if rec_exists:
                raise ValidationError(_('{} is already exists for this flock: {}'.format('Hose', rec_exists.flock_id.display_name)))

    @api.multi
    def write(self, vals):
        for rec in self:
            rec.cek_duplicate_house_id(vals)
        rec = super(WorkOrder, self).write(vals)
        return rec

    @api.multi
    @api.returns(None, lambda value: value[0])
    def copy_data(self, default=None):
        result = super(WorkOrder, self).copy_data(default)

        for one in result:
            if 'house_id' in one:
                del(one['house_id'])

        return result

    @api.multi
    def action_breeding_list(self):
        ctx = {
            'default_work_order_id': self.id,
        }

        model_name = 'berdikari.breeding.input'
        model = self.env[model_name]
        if len(self.line_breed_ids) == 1:
            rec = model.search([('work_order_id', '=', self.id)], limit=1)
            res_id = False
            if rec:
                res_id = rec.id

            action = Util.jek_open_form(
                self, model_name=model_name, id=res_id, ctx=ctx
            )
        else:
            domain = [('work_order_id','=',self.id)]
            action = Util.jek_redirect_to_model(
                title='Breeding', model_name=model_name, ctx=ctx, domain=domain
            )

            action = self.env.ref('berdikari.breeding_input_list_action').read()[0]
            action['domain'] = domain

        return action

    @api.multi
    def action_breeding_input(self):
        ctx = {
            'default_work_order_id': self.id,
        }

        model_name = 'berdikari.breeding.input'
        # model = self.env[model_name]
        # rec = model.search([('work_order_id', '=', self.id)], limit=1)
        # res_id = False
        # if rec:
        #     res_id = rec.id

        res_id = False
        action = Util.jek_open_form(
            self, model_name=model_name, id=res_id, ctx=ctx
        )
        return action


    @api.multi
    def action_setter_list(self):
        ctx = {
            'default_work_order_id': self.id,
        }

        model_name = 'berdikari.fms.grading.setter'
        model = self.env[model_name]
        if len(self.line_breed_ids) == 1:
            rec = model.search([('work_order_id', '=', self.id)], limit=1)
            res_id = False
            if rec:
                res_id = rec.id

            action = Util.jek_open_form(
                self, model_name=model_name, id=res_id, ctx=ctx
            )
        else:
            action = Util.jek_redirect_to_model(
                title='Setter', model_name=model_name, ctx=ctx, domain=[('work_order_id','=',self.id)]
            )
        return action

    @api.multi
    def action_setter_input(self):
        ctx = {
            'default_work_order_id': self.id,
        }

        model_name = 'berdikari.fms.grading.setter'
        res_id = False
        action = Util.jek_open_form(
            self, model_name=model_name, id=res_id, ctx=ctx
        )
        return action


    @api.multi
    def action_hatcher_list(self):
        ctx = {
            'default_work_order_id': self.id,
        }

        model_name = 'berdikari.fms.grading.hatcher'
        model = self.env[model_name]
        if len(self.line_breed_ids) == 1:
            rec = model.search([('work_order_id', '=', self.id)], limit=1)
            res_id = False
            if rec:
                res_id = rec.id

            action = Util.jek_open_form(
                self, model_name=model_name, id=res_id, ctx=ctx
            )
        else:
            action = Util.jek_redirect_to_model(
                title='Hatcher', model_name=model_name, ctx=ctx, domain=[('work_order_id','=',self.id)]
            )
        return action

    @api.multi
    def action_hatcher_input(self):
        ctx = {
            'default_work_order_id': self.id,
        }

        model_name = 'berdikari.fms.grading.hatcher'
        res_id = False
        action = Util.jek_open_form(
            self, model_name=model_name, id=res_id, ctx=ctx
        )
        return action


    @api.multi
    def update_age_daily(self, set_to_this_date = False):
        for rec in self:
            work_order_id = rec.id
            old_phase_id_id = rec.current_phase_id.id
            new_phase_id_id = False
            old_stock = {}

            start_date = rec.start_date
            date_1 = start_date

            if set_to_this_date:
                date_today = set_to_this_date
            else:
                date_today = fields.Date.today()

            if date_1 and rec.state == 'open':
                current_age = date_today - date_1
                current_age = int(current_age.days/7) + (current_age.days % 7 > 0)
                rec.current_age = current_age #weeks

                next_phase_min = 0
                #kenapa butuh looping line_breed_ids? karena butuh tahu urutan phase yang dipakai
                for one in rec.line_breed_ids:
                    #jika current_age = masuk ke new phase
                    if current_age >= next_phase_min and current_age <= one.std_duration:
                        if old_phase_id_id != one.phase_id.id:
                            new_phase_id_id = one.phase_id.id #ini adalah phase baru
                            rec.current_phase_id = new_phase_id_id
                    next_phase_min = one.std_duration + 1

                    if old_phase_id_id == one.phase_id.id:
                        old_stock[one.asset_id.id] = one
                        # old_stock[one.asset_id.id] = one.avail_qty
                        # old_stock['one_{}'.format(one.asset_id.id)] = one

                    else:
                        if new_phase_id_id == one.phase_id.id:
                            # one.avail_qty = old_stock[one.asset_id.id]
                            old_one = old_stock[one.asset_id.id]
                            one.avail_qty = old_one.avail_qty
                            old_one.avail_qty = 0

                    if one.phase_id.id == rec.setup_phase_production_id.id:
                        prod_week = one.std_duration
                        rec.flock_id.write({'prod_week' : prod_week})

            rec.flock_id.write({
                'start_date': rec.start_date,
                'duration': rec.duration,
                'end_date': rec.end_date,
                'current_age': rec.current_age,
                'current_phase_id': rec.current_phase_id.id,
            })

    @api.multi
    def compute_today(self):
        for rec in self:
            rec.today = fields.Date.today()
    today = fields.Date(compute= compute_today)


    @api.onchange('product_product_id')
    def onchange_product_product_id(self):
        for rec in self:
            rec.uom_id = rec.product_product_id.product_tmpl_id.uom_id

    def compute_is_invisible_breeding_input_button(self):
        for rec in self:
            is_hide = True
            if not rec.flock_state == 'closed':
                user = self.env.user
                if user and \
                    user.employee_id and \
                    user.employee_id.department_id and \
                    user.employee_id.department_id.is_allow_input_breeding and \
                    rec.state == 'approved' and \
                    rec.is_bio_use:
                        is_hide = False
            # print('################### AAAAAAAAAAAAAAAAAAAAA user and ', user )
            # print('################### AAAAAAAAAAAAAAAAAAAAA user.employee_id and ', user.employee_id )
            # print('################### AAAAAAAAAAAAAAAAAAAAA user.employee_id.department_id and ', user.employee_id.department_id )
            # print('################### AAAAAAAAAAAAAAAAAAAAA user.employee_id.department_id.is_allow_input_breeding and ', user.employee_id.department_id.is_allow_input_breeding )
            # print('################### AAAAAAAAAAAAAAAAAAAAA rec.state == approved ', rec.state == 'approved' )
            # print('################### AAAAAAAAAAAAAAAAAAAAA rec.is_bio_use', rec.is_bio_use)
            # print('################### AAAAAAAAAAAAAAAAAAAAA is_hide = Fals', is_hide)

            rec.is_invisible_breeding_input_button = is_hide
    is_invisible_breeding_input_button = fields.Boolean(compute=compute_is_invisible_breeding_input_button)


    def compute_is_invisible_setter_input_button(self):
        for rec in self:
            is_hide = True
            if not rec.flock_state == 'closed':
                if rec.count_breeding > 0:
                    user = self.env.user
                    if user and user.employee_id and user.employee_id.department_id and user.employee_id.department_id.is_allow_input_setter:
                        is_hide = False
            rec.is_invisible_setter_input_button = is_hide 
    is_invisible_setter_input_button = fields.Boolean(compute=compute_is_invisible_setter_input_button)


    def compute_is_invisible_hatcher_input_button(self):
        for rec in self:
            is_hide = True
            if not rec.flock_state == 'closed':
                if rec.count_setter > 0:
                    user = self.env.user
                    if user and user.employee_id and user.employee_id.department_id and user.employee_id.department_id.is_allow_input_hatcher:
                        is_hide = False
            rec.is_invisible_hatcher_input_button = is_hide 
    is_invisible_hatcher_input_button = fields.Boolean(compute=compute_is_invisible_hatcher_input_button)


class WorkOrderLineBreed(models.Model):
    _name = 'berdikari.work.order.line.breed'
    _rec_name = 'asset_id'

    work_order_id = fields.Many2one('berdikari.work.order')
    work_order_state = fields.Selection([('draft', 'Draft'),('open', 'Open'),], related='work_order_id.state')

    flock_id = fields.Many2one('berdikari.flock.master', related='work_order_id.flock_id', store=True)
    first_phase_id = fields.Many2one('berdikari.phase', related='work_order_id.first_phase_id')
    operating_unit_id = fields.Many2one('operating.unit', string=" Unit", related='flock_id.operating_unit_id', store=True)

    # @api.onchange('flock_id','operating_unit_id')
    # def onchange_domain_house(self):
    #     domain = {}
    #     operating_unit_id = self.flock_id.operating_unit_id.id
    #     if operating_unit_id:
    #         domain_house = [('operating_unit_id', '=', operating_unit_id)]
    #         domain['house_id'] = domain_house
    #     hasil = {'domain': domain}
    #     return hasil
    #
    # def default_domain_house(self):
    #     domain = []
    #     operating_unit_id = self.operating_unit_id.id
    #     if operating_unit_id:
    #         domain.append(('operating_unit_id', '=', operating_unit_id))
    #     # domain = [('operating_unit_id', '=', operating_unit_id)]
    #     return domain
    house_id = fields.Many2one('berdikari.chicken.coop', string='House', domain = "[('operating_unit_id', '=', operating_unit_id)]")

    phase_id = fields.Many2one('berdikari.phase')

    asset_used_id = fields.Many2one('account.asset.asset.used')

    def compute_is_phase_pertama(self):
        for rec in self:
            rec.is_phase_pertama = rec.phase_id.id == rec.work_order_id.first_phase_id.id
    is_phase_pertama = fields.Boolean(compute=compute_is_phase_pertama)

    @api.onchange('phase_id')
    def onchange_phase_id(self):
        self.std_duration = self.phase_id.duration
    std_duration = fields.Integer(string='Std Duration (weeks)')

    asset_id = fields.Many2one('account.asset.asset', domain="[('flock_id', '=', flock_id)]")
    asset_avail_qty = fields.Integer(related='asset_id.avail_qty', string="Unused Asset")
    lot_id = fields.Many2one('stock.production.lot', string='Lot/ Serial Number', related='asset_id.lot_id', store=True)
    # lot_id = fields.Many2one('stock.production.lot', string='Lot/ Serial Number', store=True)

    # asset_id = fields.Many2one('account.asset.asset')
    asset_categ_id = fields.Many2one('account.asset.category', related='asset_id.category_id')
    sex = fields.Selection(selection=[('male', 'Male'),('female', 'Female')], related='asset_id.sex')

    # asset_type = fields.Selection([('consu', 'Consumable'),
    #     ('service', 'Service'),
    #     ('product', 'Storable Product')], related='asset_id.type')
    planning_qty_line = fields.Integer()
    uom_id = fields.Many2one('uom.uom', related='asset_id.uom_id', store=True)


    biologis_used_id = fields.Many2one('berdikari.asset.biologis.used')
    death_qty = fields.Integer(string='Death', store=True)
    # avail_qty = fields.Integer(related='biologis_used_id.last_qty', store=True)
    avail_qty = fields.Integer(store=True)

    @api.multi
    def action_biological_used(self):
        model_name = 'berdikari.asset.biologis.used'
        model = self.env[model_name]

        for rec in self:
            ctx = {}
            domain = []
            res_id = False

            if rec.biologis_used_id:
                res_id = rec.biologis_used_id.id
            else:
                if rec.work_order_id and rec.asset_id:
                    ctx['default_work_order_id'] = rec.work_order_id.id
                    ctx['default_work_order_line_breed_id'] = rec.id
                    ctx['default_asset_id'] = rec.asset_id.id

                    domain.append(('work_order_line_breed_id', '=', rec.id))
                    rec = model.search(domain, limit=1)
                    if rec:
                        res_id = rec.id
            action = Util.jek_open_form(self, model_name=model_name, id=res_id, ctx=ctx)
            return action

    @api.multi
    def is_invisible_button_bio_use(self):
        for rec in self:
            int_bio_use = 0
            is_visible = True
            if not rec.id:
                is_visible = False
                int_bio_use = 1
            if not rec.is_phase_pertama:
                is_visible = False
                int_bio_use = 2
            # if rec.work_order_state != 'draft':
            #     is_visible= False
            #     int_bio_use = 3
            if rec.work_order_id.last_breeding_id:
                is_visible= False
                int_bio_use = 4
            if rec.work_order_id.is_bio_use:
                is_visible= False
                int_bio_use = 6

            phase_pertama_id = False
            row_setup = self.env['jekdoo.setup'].search([], limit=1, order="id desc")
            if row_setup and row_setup.phase_pertama_id:
                phase_pertama_id = row_setup.phase_pertama_id
            if phase_pertama_id:
                if rec.phase_id.id != phase_pertama_id.id:
                    is_visible= False
                    int_bio_use = 5

            rec.is_invisible_button_bio_use = int_bio_use
            rec.int_bio_use = str(int_bio_use)

    is_invisible_button_bio_use = fields.Integer(compute=is_invisible_button_bio_use)
    int_bio_use = fields.Integer()

    @api.onchange('asset_id')
    def onchange_asset_id_1(self):
        for rec in self:
            rec.planning_qty_line = rec.asset_avail_qty


class WorkOrderLineFeed(models.Model):
    _name = 'berdikari.work.order.line.feed'
    _rec_name = 'product_template_id'

    work_order_id = fields.Many2one('berdikari.work.order')
    product_product_id = fields.Many2one('product.product', String='Feed')
    product_template_id = fields.Many2one('product.template', String='Feed', related='product_product_id.product_tmpl_id')
    product_template_code = fields.Char(related='product_template_id.default_code', string='Feed Code')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    sex = fields.Selection(selection=[('male', 'Male'),('female', 'Female')], related='product_template_id.sex', store=True)
    material_planning_qty_line = fields.Integer()
    uom_id = fields.Many2one('uom.uom', string='UOM', related='product_template_id.uom_id', store=True)
    avail_qty = fields.Float(related='product_template_id.qty_available', string='Avail Qty')


class WorkOrderLineOVK(models.Model):
    _name = 'berdikari.work.order.line.ovk'

    work_order_id = fields.Many2one('berdikari.work.order')
    product_product_id = fields.Many2one('product.product', String='Feed')
    product_template_id = fields.Many2one('product.template', String='Feed', related='product_product_id.product_tmpl_id')
    product_template_code = fields.Char(related='product_template_id.default_code', string='Mat Code')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    material_planning_qty_line = fields.Integer()
    uom_id = fields.Many2one('uom.uom', string='UOM', related='product_template_id.uom_id', store=True)
    avail_qty = fields.Float(related='product_template_id.qty_available', string='Avail Qty')


class WorkOrderLineByproduct(models.Model):
    _name = 'berdikari.work.order.line.byproduct'

    work_order_id = fields.Many2one('berdikari.work.order')
    product_product_id = fields.Many2one('product.product', String='Product')
    product_template_id = fields.Many2one('product.template', String='Product', store=True, related='product_product_id.product_tmpl_id')
    product_template_code = fields.Char(related='product_template_id.default_code', string='Product Code')
    uom_id = fields.Many2one('uom.uom', string='UOM', related='product_template_id.uom_id', store=True)
    is_result = fields.Boolean(string='Is Result')
    daily_target = fields.Integer(string='Daily Target')


class WorkOrderLineByproductSetter(models.Model):
    _name = 'berdikari.work.order.line.byproduct.setter'

    work_order_id = fields.Many2one('berdikari.work.order')
    product_product_id = fields.Many2one('product.product', String='Product')
    product_template_id = fields.Many2one('product.template', String='Product Template', related='product_product_id.product_tmpl_id')
    product_template_code = fields.Char(related='product_template_id.default_code', string='Product Code')
    uom_id = fields.Many2one('uom.uom', string='UOM', related='product_template_id.uom_id', store=True)
    is_result = fields.Boolean(string='Is Result')
    daily_target = fields.Integer(string='Daily Target')


class WorkOrderLineByproductHatcher(models.Model):
    _name = 'berdikari.work.order.line.byproduct.hatcher'

    work_order_id = fields.Many2one('berdikari.work.order')
    product_product_id = fields.Many2one('product.product', String='Product')
    product_template_id = fields.Many2one('product.template', String='Product Template', related='product_product_id.product_tmpl_id')
    product_template_code = fields.Char(related='product_template_id.default_code', string='Product Code')
    uom_id = fields.Many2one('uom.uom', string='UOM', related='product_template_id.uom_id', store=True)
    is_result = fields.Boolean(string='Is Result')
    daily_target = fields.Integer(string='Daily Target')


class WorkOrderLineCurrentProduct(models.Model):
    _name = 'berdikari.work.order.line.current.product'

    work_order_id = fields.Many2one('berdikari.work.order')
    product_template_id = fields.Many2one('product.template', String='Product')
    product_template_code = fields.Char(related='product_template_id.default_code', string='Product Code')
    uom_id = fields.Many2one('uom.uom', string='UOM')
    qty = fields.Integer(string='Available QTY')

