# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.jekdoo.utils.util import Util
import datetime
from dateutil import relativedelta
from odoo.exceptions import ValidationError


class FlockMaster(models.Model):
    _name = 'berdikari.flock.master'
    _description = 'Berdikari Flock Master'

    _sql_constraints = [
        ('uniq_name', 'unique(name)', _('Name already exists!')),
    ]

    code = fields.Char(string='Code', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.flock.master'))

    def default_name(self):
        tahunbulan = datetime.datetime.now().strftime('%Y%m')
        name = 'Flock {}'.format(tahunbulan)
        return name
    name = fields.Char(required=True, default=default_name)

    #ini depreceated, akan segera dihapus abis commit push sama kerjaan vinny
    src_company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    purchase_id = fields.Many2one('purchase.order', string='Purchase Order')
    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)

    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)

    def default_year(self):
        ret = datetime.datetime.now().strftime('%Y')
        return ret

    @api.depends('period_year')
    @api.onchange('period_year')
    def onchange_year(self):
        for rec in self:
            allow_char = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
            if any(x not in allow_char for x in rec.period_year):
                raise ValidationError(_("Invalid Year"))
    period_year = fields.Char(required=True, default=default_year)

    def default_sequence(self):
        ret = datetime.datetime.now().strftime('%m')
        return ret
    period_sequence = fields.Integer(required=True, default=default_sequence)

    @api.onchange('start_date')
    def onchange_start_date(self):
        # date_1 = datetime.datetime.strptime(start_date, "%m/%d/%y")
        date_1 = self.start_date
        if date_1:
            end_date = date_1 + relativedelta.relativedelta(months =+ 18)
            self.end_date = end_date

    start_date = fields.Date()
    duration = fields.Integer(string='Duration (weeks)')
    end_date = fields.Date()
    current_age = fields.Integer(string='Current Age (weeks)', readonly=True)
    current_phase_id = fields.Many2one('berdikari.phase', readonly=True)

    @api.onchange('start_date', 'duration', 'line_breed_ids')
    @api.depends('start_date', 'duration', 'line_breed_ids')
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


    def compute_all_day_qty(self):
        for rec in self:
            rec.all_day_qty = rec.duration * 7
    all_day_qty = fields.Integer(compute=compute_all_day_qty)

    def compute_current_day(self):
        for rec in self:
            current_day = 0
            if rec.start_date:
                rec.current_day= (fields.Date.today() - rec.start_date).days
    current_day= fields.Integer(compute=compute_current_day)

    prod_week = fields.Integer(string='Production Week')

    def compute_prod_day_start(self):
        for rec in self:
            if rec.prod_week:
                rec.prod_day_start = ((rec.prod_week - 1) * 7 ) + 1
    prod_day_start= fields.Integer(compute=compute_prod_day_start)

    def compute_prod_day_qty(self):
        for rec in self:
            if rec.current_day and rec.duration:
                rec.prod_day_qty = (rec.duration - (rec.current_day - 1) ) * 7
    prod_day_qty = fields.Integer(compute=compute_prod_day_qty)

    def compute_prod_day_qty_current(self):
        for rec in self:
            if rec.current_day > rec.prod_day_start:
                rec.prod_day_qty_current = (rec.current_day - rec.prod_day_start) + 1
    prod_day_qty_current = fields.Integer(compute=compute_prod_day_qty_current, string='Prod Day')

    def compute_prod_day_left(self):
        for rec in self:
            if rec.prod_day_qty:
                rec.prod_day_left = rec.prod_day_qty - (rec.prod_day_qty_current - 0)
    prod_day_left = fields.Integer(compute=compute_prod_day_left)


    notes = fields.Text()
    state = fields.Selection([('open','Open'), ('closed', 'Closed')], default='open')

    def compute_is_invisible_close_button(self):
        for rec in self:
            is_hide = True
            user = self.env.user
            if user and \
                user.employee_id and \
                user.employee_id.job_id and \
                user.employee_id.job_id.is_allow_close_flock:
                    is_hide = rec.state == 'closed'
            rec.is_invisible_close_button = is_hide
    is_invisible_close_button = fields.Boolean(compute=compute_is_invisible_close_button)

    @api.multi
    def action_close_flock(self):

        self.state = 'closed'

        return Util.jek_pop1(_('Done'))

    # biological_assets = fields.Many2one('product.template')
    biological_asset_ids = fields.One2many('berdikari.flock.master.assets', 'flock_id')

    work_order_ids = fields.One2many('berdikari.work.order', 'flock_id')

    def compute_is_allow_create_wo(self):
        for rec in self:
            ok = False
            if self.env.user.job_id:
                job_id = self.env.user.job_id
                ok = job_id.is_allow_create_wo
            rec.is_allow_create_wo = ok
    is_allow_create_wo = fields.Boolean(compute=compute_is_allow_create_wo)

    def compute_count_work_order(self):
        for rec in self:
            rec.count_work_order = len(rec.work_order_ids)
    count_work_order = fields.Integer(compute=compute_count_work_order, )

    @api.multi
    def action_work_order_list(self):
        ctx = {
            'default_flock_id': self.id,
        }

        model_name = 'berdikari.work.order'
        model = self.env[model_name]
        if len(self.work_order_ids) == 1:
            rec = model.search([('flock_id', '=', self.id)], limit=1)
            res_id = False
            if rec:
                res_id = rec.id

            action = Util.jek_open_form(
                self, model_name=model_name, id=res_id, ctx=ctx
            )
        else:
            action = Util.jek_redirect_to_model(
                title='Work Order', model_name=model_name, ctx=ctx, domain=[('flock_id','=',self.id)]
            )
        return action

    @api.multi
    def action_work_order_input(self):

        if not (self.start_date and self.end_date and self.duration):
            raise ValidationError(_('Start Date, End Date, and Duration may not be empty!'))

        ctx = {
            'default_flock_id': self.id,
        }

        model_name = 'berdikari.work.order'
        # model = self.env[model_name]
        # rec = model.search([('flock_id', '=', self.id)], limit=1)
        # res_id = False
        # if rec:
        #     res_id = rec.id

        res_id = False
        action = Util.jek_open_form(
            self, model_name=model_name, id=res_id, ctx=ctx
        )
        return action

    @api.multi
    def action_hachery(self):
        ctx = {
            'default_flock_id': self.id,
        }

        model_name = 'berdikari.fms.hatchery'
        model = self.env[model_name]
        rec = model.search([('flock_id','=',self.id)], limit=1)
        res_id = False
        if rec:
            res_id = rec.id

        action = Util.jek_open_form(
            self, model_name=model_name, id=res_id, ctx=ctx
        )
        print(action)
        return action


class FlockAsses(models.Model):
    _name = 'berdikari.flock.master.assets'
    _description = 'Result Flock'
    _rec_name = 'product_template_id'

    flock_id = fields.Many2one('berdikari.flock.master')
    product_template_id = fields.Many2one('product.template', string='Results')