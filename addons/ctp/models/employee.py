# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.jekdoo.utils.util import Util
from odoo.exceptions import ValidationError
from datetime import datetime, date


class Employee(models.Model):
    _inherit = 'hr.employee'
    _description = 'Inherit HR Employee'

    #function simpan addnew
    #return new record
    @api.model
    def create(self, vals_list):
        rec = super(Employee, self).create(vals_list)
        if 'user_id' in vals_list:
            user_id = vals_list.get('user_id') #dapetnya ID doang ( integer)
            if user_id: #jika ada, bukan 0 atau false /null
                model_users = self.env['res.users'] #create instance model hr_employee
                rec_user = model_users.search([('id','=',user_id)]) #lakukan pencarian, yang id = user_id
                rec_user.write({'employee_id':rec.id})

                rec_user = model_users.search([('name','like','andi')]) #Andi malarangeng, Andi F Noya, ANdi Subahyo
                rec_user.write({'employee_id':rec.id})

        return rec

    #function simpan edit
    #return boolean

    #vals['user_id'] = ''
    #vals['email'] = 'adelia@gmail.com'
    @api.multi
    def write(self, vals):
        model_users = self.env['res.users']  # create instance model hr_employee
        for rec in self:
            if 'user_id' in vals:
                user_id = vals.get('user_id')
                if not user_id: #tadinya ada, di edit jadi kosong / menghapus relasi dengan user
                    user_id = rec.user_id #return bukan ID integer doang, tapi record (model) res.users
                    if user_id:
                        user_id.write({'employee_id':False})
                else: #jika tadinya kosong, sekarang di set = employee
                    rec_user = model_users.search([('id', '=', user_id)])  # lakukan pencarian, yang id = user_id
                    if rec_user:
                        rec_user.write({'employee_id': rec.id})
        return super(Employee, self).write(vals)

    # employee_id = fields.Char(string='Employee ID')
    job_level_id = fields.Many2one('berdikari.hr.job.level', string='Job Level', store=True)
    employee_status = fields.Selection([('probation', 'Probation'), ('permanent', 'Permanent'), ('contract', 'Contract'), ('quit', 'Quit')])
    employee_status_date = fields.Date()
    age = fields.Float()
    religion_id = fields.Many2one('berdikari.religion', string='Religion', store=True)
    tax_marital_status = fields.Selection([('tk','TK'),('k0','K0'),('k1','K1'),('k2','K2'),('k3','K3'),('k4','K4')])
    address = fields.Text()
    residence_address = fields.Text()
    province = fields.Char()
    ethnic = fields.Char()
    postal_code = fields.Integer()
    home_phone = fields.Char()
    mobile_phone = fields.Char(string='Phone 1')
    mobile_phone_2 = fields.Char(string='Phone 2')
    personal_email = fields.Char()
    education_level_id = fields.Many2one('berdikari.hr.education.level', string='Education Level', store=True)
    faculty = fields.Char()
    study = fields.Char()
    year_graduate = fields.Integer()
    grade_point = fields.Float()
    id_no_expired_date = fields.Date()
    drive_licence_type = fields.Char()
    drive_licence_id = fields.Char(string='Drive Licence ID')
    drive_licence_exp_date = fields.Date()
    passport_place_of_issued = fields.Char(string='Passport Place of Issued')
    passport_exp_date = fields.Date(string='Passport Exp. Date')
    npwp = fields.Char(string='NPWP')
    npwp_address = fields.Text(string='NPWP Address')
    bank_payroll_account = fields.Char()
    # bank_payroll_holder = fields.Many2one('account.journal')
    # bank_mandiri_branch = fields.Char()
    other_bank_account = fields.Char()
    # other_bank_holder = fields.Many2one('account.journal')
    # other_bank_name = fields.Char()
    # other_bank_branch = fields.Char()
    bpjs_ketenagakerjaan = fields.Char(string='BPJS Ketenagakerjaan')
    kartu_jaminan_pensiun = fields.Char()
    bpjs_kesehatan = fields.Char(string='BPJS Kesehatan')
    faskes_tingkat_1 = fields.Char()
    kelas_rawat = fields.Selection([('kelas 1','Kelas 1'),('kelas 2','Kelas 2'),('kelas 3','Kelas 3')])
    tanggungan_perusahaan = fields.Float()
    bni_life = fields.Char(string='BNI Life')
    # hr_notes = fields.Text()
    operating_unit_id = fields.Many2one('operating.unit', string='Unit',
                                        default=lambda self: self.env.user.default_operating_unit_id)

    def def_compute_unit_id(self):
        for rec in self:
            rec.unit_id = rec.operating_unit_id
    unit_id = fields.Many2one('operating.unit', compute=def_compute_unit_id)


    join_date = fields.Date()
    termination_date = fields.Date()
    appraisal_ids = fields.One2many('berdikari.hr.employee.appraisal','employee_id')
    education_ids = fields.One2many('berdikari.hr.employee.education', 'employee_id')
    training_ids = fields.One2many('berdikari.hr.employee.training', 'employee_id')

    no_kartu_keluarga = fields.Char(string='Nomor Kartu Keluarga')
    birth_mother_name = fields.Char(string='Nama Ibu Kandung')
    fam_ref_name = fields.Char(string='Name')
    fam_ref_relation = fields.Many2one('berdikari.hr.family.relation', store=True, string='Family Relation')
    fam_ref_job = fields.Char(string='Job')
    fam_ref_address = fields.Char(string='Address')
    fam_ref_phone = fields.Char(string='Phone')
    fam_ref_mobile_phone = fields.Integer(string='Mobile Phone')
    family_ids = fields.One2many('berdikari.hr.employee.family', 'employee_id')

    emergency_contact_ids = fields.One2many('berdikari.hr.employee.emergency.contact', 'employee_id')
    work_ids = fields.One2many('berdikari.hr.employee.work', 'employee_id')
    medical_ids = fields.One2many('berdikari.hr.employee.medical', 'employee_id')
    reward_ids = fields.One2many('berdikari.hr.employee.reward', 'employee_id')
    punishment_ids = fields.One2many('berdikari.hr.employee.punishment', 'employee_id')
    emp_notes_ids = fields.One2many('berdikari.hr.employee.notes', 'employee_id')

    director_id = fields.Many2one('hr.employee', string='Director', related='parent_id.parent_id')
    officer_ids = fields.One2many('hr.employee', 'parent_id', string='Officers')


    @api.depends('user_id')
    @api.onchange('user_id')
    def onchange_user_id(self):
        for rec in self:
            if rec.user_id:
                rec.partner_id = rec.user_id.partner_id
            else:
                rec.partner_id = False
    partner_id = fields.Many2one('res.partner', string='Related Partner')

    #
    # def default_pr_name(self):
    #     pr_name = 'empty'
    #
    #     ctx = self._context
    #     if 'pr_name' in ctx:
    #         pr_name = ctx.get('pr_name')
    #
    #     return pr_name
    # pr_name = fields.Char(default=default_pr_name)

    @api.multi
    def action_view_paklaring(self):
        return self.env.ref('berdikari.report_paklaring').report_action(self)

    @api.multi
    def action_create_paklaring(self):
        termination_date = self.termination_date
        if not termination_date:
            raise ValidationError(_('Tgl Keluar harus diisi dulu, sebelum membuat Paklaring'))

        model_paklaring = self.env['berdikari.hr.employee.paklaring']
        setup = self.env['jekdoo.setup'].get_setup()
        dept_head_hr_id = setup.dept_head_hr_id
        if dept_head_hr_id:
            my_user = dept_head_hr_id.user_id
            my_employee = dept_head_hr_id
            my_job = my_employee.job_id
        else:
            raise ValidationError(_('Please Set Dept Head HR'))
        # my_user = self.env.user
        # my_employee = my_user.employee_id
        # my_job = my_employee.job_id
        import datetime
        vals = {
            'employee_id': self.id,
            'nomor_pegawai': self.barcode,
            'employee_last_position': self.job_id,
            'employee_address': self.address,
            'created_date': datetime.datetime.today(),
            'user_id': my_employee.id,
            'user_job_id': my_job.id if my_job else False,
        }
        if self.paklaring_id.id:
            paklaring = model_paklaring.write(vals)
        else:
            paklaring = model_paklaring.create(vals)
            self.paklaring_id = paklaring.id

        return Util.jek_pop1('Done')

    @api.multi
    def btnCashAdvance(self):
        pesan = 'pop up cash advance'
        return Util.jek_pop1(pesan)

    # produk_id = input
    # qty =
    # harga =
    #
    # @api.depends('qty', 'harga')
    # def compute_sub_total(self):
    #     for rec in self:
    #         rec.sub_total = rec.qty * rec.harga
    # sub_total = fields.Float(compute=compute_sub_total, store=True)

    paklaring_id = fields.Many2one('berdikari.hr.employee.paklaring', readonly=True, string='Paklaring')
    jabatan_pertama = fields.Many2one('hr.job', readonly=True) #inherit def create, isi ini dengan job_id /// atau jika on create kosong, on write berarti isi
    # tgl_masuk = fields.Date()
    # tgl_keluar = fields.Date()

    @api.multi
    def action_leave_carry_over(self):
        model_leave_carry_over = self.env['berdikari.leave.carry.over']
        today = datetime.now()
        leave_period_year = today.year + 1
        check_date = date(today.year, today.month, today.day)
        leave_period_date = date(leave_period_year, 1, 1)
        ctx = {
            'default_employee_id': self.id,
            'default_leave_to_carry_over_period': str(leave_period_year) if check_date == leave_period_date else str((today.year - 1)),
        }
        model_name = 'berdikari.leave.carry.over'
        domain = [('employee_id', '=', self.id)]
        return Util.jek_redirect_to_model(model_name, 'Leave Carry Over', ctx, domain=domain)

    @api.multi
    def action_cash_advance(self):
        ctx = {
            'default_partner_id': self.id,
        }
        model_name = 'account.invoice'
        domain = [('partner_id', '=', self.id)]
        return Util.jek_redirect_to_model(model_name, 'Employee Cash Advance', ctx, domain=domain)

    def compute_count_leave_carry_over(self):
        for rec in self:
            model_carry_over = self.env['berdikari.leave.carry.over']
            leave_carry_over = model_carry_over.search([('employee_id', '=', rec.id)])
            rec.count_leave_carry_over = len(leave_carry_over)
    count_leave_carry_over = fields.Integer(compute=compute_count_leave_carry_over)

    #tambahan untuk tab appraisal
    direksi_id = fields.Many2one('hr.employee')
    dept_head_id = fields.Many2one('hr.employee')

    @api.depends('parent_id')
    @api.onchange('parent_id')
    def onchange_parent_id(self):
        if not self.expense_manager_id:
            #set expense_manager_id
            expense_manager_id = self.parent_id.user_id.id
            self.expense_manager_id = expense_manager_id

class EmployeeNotes(models.Model):
    _name = 'berdikari.hr.employee.notes'
    _description = 'Berdikari Employee Notes'

    employee_id = fields.Many2one('hr.employee')
    date = fields.Date()
    notes = fields.Text()


class Department(models.Model):
    _inherit = 'hr.department'
    _description = 'Inherit HR Department'

    is_purchase_approval = fields.Boolean(string='Is Purchase Approval', default=False)
    purchase_request_type = fields.Selection(selection=[('1', 'Umum'), ('2', 'Asset'), ('3', 'Operational')])