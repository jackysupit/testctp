# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from datetime import datetime, date, time
from dateutil import relativedelta
from odoo.addons import decimal_precision as dp
from pytz import timezone
from odoo.addons.jekdoo.utils.util import Util
from odoo.exceptions import ValidationError


class HRPayslip(models.Model):
    _inherit = "hr.payslip"
    _description = 'Inherit HR Payslip'

    period_id = fields.Many2one('berdikari.hr.attendance.period', string='Period Name')

    @api.depends('period_id')
    @api.onchange('period_id')
    def onchange_domain_seq(self):
        domain = {}
        period_id = self.period_id.id
        if period_id:
            domain_seq = [('attendance_period_id', '=', period_id)]
            domain['period_seq_id'] = domain_seq
        hasil = {'domain': domain}
        return hasil

    period_seq_id = fields.Many2one('berdikari.hr.attendance.period.line', string='Period Sequence')

    @api.depends('period_seq_id')
    @api.onchange('period_seq_id')
    def onchange_period_seq(self):
        for rec in self:
            period_seq_id = rec.period_seq_id.id
            model_period_line = self.env['berdikari.hr.attendance.period.line']
            if period_seq_id:
                period_line = model_period_line.search([('id', '=', period_seq_id)], limit=1)
                rec.date_from = period_line.date_from
                rec.date_to = period_line.date_to

    date_from = fields.Date(string='Date From', readonly=True, default=False)
    # default=lambda self: fields.Date.to_string(date.today().replace(day=1)))
    date_to = fields.Date(string='Date To', readonly=True, default=False)
    # default=lambda self: fields.Date.to_string(
    #     (datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()))

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid))
    attendance_days_line_ids = fields.One2many('berdikari.hr.payslip.overtime', 'payslip_id',
                                               string='Payslip Overtime', copy=True, readonly=True,
                                               states={'draft': [('readonly', False)]})
    hr_dept_head_id = fields.Many2one('hr.employee')
    hr_dept_head_job_id = fields.Many2one('hr.job')

    @api.multi
    def compute_sheet(self):
        for payslip in self:
            number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
            # delete old payslip lines
            payslip.line_ids.unlink()
            # set the list of contract for which the rules have to be applied
            # if we don't give the contract, then the rules to apply should be for all current contracts of the employee

            date_from = self._context.get('date_from') or payslip.date_from
            date_to = self._context.get('date_to') or payslip.date_to
            period_id = self._context.get('period_id') or payslip.period_id
            period_seq_id = self._context.get('period_seq_id') or payslip.period_seq_id

            payslip.period_id = period_id
            payslip.period_seq_id = period_seq_id
            payslip.date_from = date_from
            payslip.date_to = date_to

            contract_ids = payslip.contract_id.ids or \
                           self.get_contract(payslip.employee_id, date_from, date_to)

            lines = [(0, 0, line) for line in self._get_payslip_lines(contract_ids, payslip.id)]

            payslip.write({'line_ids': lines, 'number': number})
        return True

    @api.model
    def _get_payslip_lines(self, contract_ids, payslip_id):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and \
                                                          localdict['categories'].dict[category.code] + amount or amount
            return localdict

        class BrowsableObject(object):
            def __init__(self, employee_id, dict, env):
                self.employee_id = employee_id
                self.dict = dict
                self.env = env

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                        SELECT sum(amount) as sum
                        FROM hr_payslip as hp, hr_payslip_input as pi
                        WHERE hp.employee_id = %s AND hp.state = 'done'
                        AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()[0] or 0.0

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                        SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
                        FROM hr_payslip as hp, hr_payslip_worked_days as pi
                        WHERE hp.employee_id = %s AND hp.state = 'done'
                        AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
                                FROM hr_payslip as hp, hr_payslip_line as pl
                                WHERE hp.employee_id = %s AND hp.state = 'done'
                                AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
                                    (self.employee_id, from_date, to_date, code))
                res = self.env.cr.fetchone()
                return res and res[0] or 0.0

        # we keep a dict with the result because a value can be overwritten by another rule with the same code
        result_dict = {}
        rules_dict = {}
        worked_days_dict = {}
        inputs_dict = {}
        blacklist = []
        payslip = self.env['hr.payslip'].browse(payslip_id)
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days_dict[worked_days_line.code] = worked_days_line
        for input_line in payslip.input_line_ids:
            inputs_dict[input_line.code] = input_line

        categories = BrowsableObject(payslip.employee_id.id, {}, self.env)
        inputs = InputLine(payslip.employee_id.id, inputs_dict, self.env)
        worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict, self.env)
        payslips = Payslips(payslip.employee_id.id, payslip, self.env)
        rules = BrowsableObject(payslip.employee_id.id, rules_dict, self.env)

        baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days,
                         'inputs': inputs}
        # get the ids of the structures on the contracts and their parent id as well
        contracts = self.env['hr.contract'].browse(contract_ids)
        if len(contracts) == 1 and payslip.struct_id:
            structure_ids = list(set(payslip.struct_id._get_parent_structure().ids))
        else:
            structure_ids = contracts.get_all_structures()
        # get the rules of the structure and thier children
        rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        # run the rules by sequence
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]
        sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)

        meal = 0
        transport = 0
        overtime_pay = 0
        for rec in self:
            attendance_sheet_data = self.env['berdikari.attendance.sheets'].search(
                        [('name', '=', rec.employee_id.id), ('period_start', '=', rec.date_from),
                         ('period_end', '=', rec.date_to)])
            overtime_data = self.env['berdikari.overtime.request'].search(
                [('user_id', '=', rec.employee_id.user_id.id), ('start_date', '>=', rec.date_from),
                 ('end_date', '<=', rec.date_to), ('state', '=', 'done')])

            for allowance in attendance_sheet_data.attendance_line_ids:
                meal = meal + allowance.meal_allowance
                transport = transport + allowance.transport_allowance

            if overtime_data:
                for overtime in overtime_data:
                    overtime_pay = overtime_pay + overtime.overtime_pay

            # get hr dept head
            setup = self.env['jekdoo.setup'].get_setup()
            dept_head_hr_id = setup.dept_head_hr_id
            if dept_head_hr_id:
                my_user = dept_head_hr_id.user_id
                my_employee = dept_head_hr_id
                my_job = my_employee.job_id
            else:
                raise ValidationError(_('Please Set Dept Head HR'))

            rec.hr_dept_head_id = my_employee.id
            rec.hr_dept_head_job_id = my_job.id if my_job else False

        for contract in contracts:
            # worked_days_line_ids = self.worked_days_line_ids
            employee = contract.employee_id
            localdict = dict(baselocaldict, employee=employee, contract=contract)
            for rule in sorted_rules:
                key = rule.code + '-' + str(contract.id)
                localdict['result'] = None
                if 'meal' in rule.amount_python_compute:
                    localdict['result_qty'] = meal
                elif 'transport' in rule.amount_python_compute:
                    localdict['result_qty'] = transport
                else:
                    localdict['result_qty'] = 1.0
                localdict['result_rate'] = 100
                # check if the rule can be applied
                if rule._satisfy_condition(localdict) and rule.id not in blacklist:
                    # compute the amount of the rule
                    amount, qty, rate = rule._compute_rule(localdict)
                    # check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    # set/overwrite the amount computed for this rule in the localdict
                    if 'overtime' in rule.amount_python_compute:
                        amount = overtime_pay
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    rules_dict[rule.code] = rule
                    # sum the amount for its salary category
                    localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                    # create/overwrite the rule in the temporary results
                    result_dict[key] = {
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'name': rule.name,
                        'code': rule.code,
                        'category_id': rule.category_id.id,
                        'sequence': rule.sequence,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'condition_select': rule.condition_select,
                        'condition_python': rule.condition_python,
                        'condition_range': rule.condition_range,
                        'condition_range_min': rule.condition_range_min,
                        'condition_range_max': rule.condition_range_max,
                        'amount_select': rule.amount_select,
                        'amount_fix': rule.amount_fix,
                        'amount_python_compute': rule.amount_python_compute,
                        'amount_percentage': rule.amount_percentage,
                        'amount_percentage_base': rule.amount_percentage_base,
                        'register_id': rule.register_id.id,
                        'amount': amount,
                        'employee_id': contract.employee_id.id,
                        'quantity': qty,
                        'rate': rate,
                        'account_id': rule.account_debit.id,
                    }
                else:
                    # blacklist this rule and its children
                    blacklist += [id for id, seq in rule._recursive_search_of_rules()]

        #tambahan utk overtime
        self.attendance_days_line_ids.unlink()
        for data in self:
            res = []
            overtime_data = self.env['berdikari.overtime.request'].search(
                [('user_id', '=', data.employee_id.user_id.id), ('start_date', '>=', data.date_from),
                 ('end_date', '<=', data.date_to), ('state', '=', 'done')])
            if overtime_data:
                for overtime in overtime_data:
                    ot = {
                        'name': _("Overtime"),
                        'sequence': 99,
                        'overtime_date_from': overtime.start_date,
                        'overtime_date_to': overtime.end_date,
                        'overtime_day': overtime.day,
                        'no_of_hours': overtime.numbers_of_hour,
                        'meal_provided': overtime.meal_provided,
                        'overtime_rate': overtime.overtime_pay,
                    }
                    res.append(ot)
                data.attendance_days_line_ids = res

        return list(result_dict.values())

    @api.onchange('date_from')
    def onchange_attendance(self):
        res = []
        overtime_data = self.env['berdikari.overtime.request'].search(
            [('user_id', '=', self.employee_id.user_id.id), ('start_date', '>=', self.date_from),
             ('end_date', '<=', self.date_to), ('state', '=', 'done')])
        if overtime_data:
            for overtime in overtime_data:
                ot = {
                    'name' : _("Overtime"),
                    'sequence': 99,
                    'overtime_date_from' : overtime.start_date,
                    'overtime_date_to' : overtime.end_date,
                    'overtime_day': overtime.day,
                    'no_of_hours' : overtime.numbers_of_hour,
                    'meal_provided' : overtime.meal_provided,
                    'overtime_rate' : overtime.overtime_pay,
                }
                res.append(ot)
            self.attendance_days_line_ids = res


    @api.model
    def render_qweb_html2(self, docids = None, data=None):
        """This method generates and returns html version of a report.
        """
        if not docids:
            docids = [1,2]

        if not data:
            data = {}
        report_model_name = 'berdikari.payslip_karyawan_kontrak_report'

        data.setdefault('report_type', 'html')
        data = self.env.get(report_model_name)
        return self.render_template(report_model_name, data), 'html'

    @api.model
    def render_template(self, template, values=None, engine='ir.qweb'):
        return self.browse(1).render(values, engine)

    @api.multi
    def confirm_button(self, format_report):
        docs = {}
        # format_report = self.format_report
        period_id = self.period_id
        period_seq_id = self.period_seq_id
        operating_unit_id = self.operating_unit_id
        struct_id = self.struct_id
        # ids = [1, 2]

        domain = [('operating_unit_id', '=', operating_unit_id.id),('struct_id', '=', struct_id.id), ]
        if period_id:
            domain.append(('period_id', '=', period_id.id))

        if period_seq_id:
            domain.append(('period_seq_id', '=', period_seq_id.id))

        payslip_ids = self.env['hr.payslip'].search(domain)
        ids = payslip_ids.ids

        print('############################## ids: ', ids)

        setup = self.env['jekdoo.setup'].get_setup()
        gaji_pokok_id = setup.gaji_pokok_id
        tunjangan_perumahan_id = setup.tunjangan_perumahan_id
        tunjangan_transport_id = setup.tunjangan_transport_id
        bpjs_naker_perusahaan_id = setup.bpjs_naker_perusahaan_id
        bpjs_naker_pegawai_id = setup.bpjs_naker_pegawai_id
        potongan_bpjs_kesehatan_perusahaan_id = setup.potongan_bpjs_kesehatan_perusahaan_id
        potongan_bpjs_kesehatan_pegawai_id = setup.potongan_bpjs_kesehatan_pegawai_id
        tunjangan_jabatan_id = setup.tunjangan_jabatan_id
        potongan_pinjaman_id = setup.potongan_pinjaman_id
        for one in payslip_ids:
            employee_id = one.employee_id
            employee_id_id = employee_id.id

            #  No,
            #  Nama,
            #  Gaji,
            #  Tunjangan Jabatan,
            #  Potongan Pinjaman,
            #  Total Potongan,
            #  BPJS Naker(Perusahaan),
            #  BPJS Naker(Pegawai),
            #  Total Potongan BPJS Naker,
            #  THP,
            #  Maks BPJS Kesehatan,
            #  BPJS Kesehatan(Perusahaan),
            #  BPJS Kesehatan(Pegawai),
            #  Total Potongan BPJS Kesehatan,
            #  Total Diterima
            #
            gaji_pokok = 0
            tunjangan_jabatan = 0
            potongan_pinjaman = 0
            tunjangan_perumahan = 0
            tunjangan_transport = 0
            bpjs_naker_perusahaan = 0
            bpjs_naker_pegawai = 0
            potongan_bpjs_kesehatan_perusahaan = 0
            potongan_bpjs_kesehatan_pegawai = 0
            for line in one.line_ids:
                salary_rule_id_id = line.salary_rule_id.id

                if salary_rule_id_id == gaji_pokok_id.id:
                    gaji_pokok += line.total

                if salary_rule_id_id == tunjangan_jabatan_id.id:
                    tunjangan_jabatan += line.total

                if salary_rule_id_id == potongan_pinjaman_id.id:
                    potongan_pinjaman += line.total

                if format_report == 'direksi':
                    if salary_rule_id_id == tunjangan_perumahan_id.id:
                        tunjangan_perumahan += line.total

                    if salary_rule_id_id == tunjangan_transport_id.id:
                        tunjangan_transport += line.total

                if salary_rule_id_id == bpjs_naker_perusahaan_id.id:
                    bpjs_naker_perusahaan += line.total

                if salary_rule_id_id == bpjs_naker_pegawai_id.id:
                    bpjs_naker_pegawai += line.total

                if salary_rule_id_id == potongan_bpjs_kesehatan_perusahaan_id.id:
                    potongan_bpjs_kesehatan_perusahaan += line.total

                if salary_rule_id_id == potongan_bpjs_kesehatan_pegawai_id.id:
                    potongan_bpjs_kesehatan_pegawai += line.total

            bpjs_naker_total = bpjs_naker_perusahaan + bpjs_naker_pegawai
            potongan_bpjs_kesehatan_total = potongan_bpjs_kesehatan_perusahaan + potongan_bpjs_kesehatan_pegawai

            total_diterima = 0
            total_diterima += gaji_pokok
            if format_report != 'penjaga':
                total_diterima += gaji_pokok
                total_diterima += tunjangan_jabatan
                total_diterima += potongan_pinjaman
                total_diterima += tunjangan_perumahan
                total_diterima += tunjangan_transport
                total_diterima -= bpjs_naker_total
                total_diterima -= potongan_bpjs_kesehatan_total

            total_spp = 0
            satu = {}
            satu['id'] = one.id
            satu['name'] = employee_id.name
            satu['employee_id'] = employee_id_id
            currency_id = self.env.ref('base.IDR')[0]
            satu['currency_id'] = currency_id
            # import ipdb; ipdb.set_trace()
            if employee_id_id in docs:
                dua = docs[employee_id_id]

                satu['gaji_pokok'] = dua['gaji_pokok'] + gaji_pokok
                satu['tunjangan_jabatan'] = dua['tunjangan_jabatan'] + tunjangan_jabatan
                satu['potongan_pinjaman'] = dua['potongan_pinjaman'] + potongan_pinjaman
                satu['tunjangan_perumahan'] = dua['tunjangan_perumahan'] + tunjangan_perumahan
                satu['tunjangan_transport'] = dua['tunjangan_transport'] + tunjangan_transport
                satu['bpjs_naker_perusahaan'] = dua['bpjs_naker_perusahaan'] + bpjs_naker_perusahaan
                satu['bpjs_naker_pegawai'] = dua['bpjs_naker_pegawai'] + bpjs_naker_pegawai
                satu['bpjs_naker_total'] = dua['bpjs_naker_total'] + bpjs_naker_total
                satu['potongan_bpjs_kesehatan_perusahaan'] = dua['potongan_bpjs_kesehatan_perusahaan'] + potongan_bpjs_kesehatan_perusahaan
                satu['potongan_bpjs_kesehatan_pegawai'] = dua['potongan_bpjs_kesehatan_pegawai'] + potongan_bpjs_kesehatan_pegawai
                satu['potongan_bpjs_kesehatan_total'] = dua['potongan_bpjs_kesehatan_total'] + potongan_bpjs_kesehatan_total
                satu['total_diterima'] = dua['total_diterima'] + total_diterima
                satu['total_spp'] = dua['total_spp'] + total_spp
            else:
                satu['gaji_pokok'] = gaji_pokok
                satu['tunjangan_jabatan'] = tunjangan_jabatan
                satu['potongan_pinjaman'] = potongan_pinjaman
                satu['tunjangan_perumahan'] = tunjangan_perumahan
                satu['tunjangan_transport'] = tunjangan_transport
                satu['bpjs_naker_perusahaan'] = bpjs_naker_perusahaan
                satu['bpjs_naker_pegawai'] = bpjs_naker_pegawai
                satu['bpjs_naker_total'] = bpjs_naker_total
                satu['potongan_bpjs_kesehatan_perusahaan'] = potongan_bpjs_kesehatan_perusahaan
                satu['potongan_bpjs_kesehatan_pegawai'] = potongan_bpjs_kesehatan_pegawai
                satu['potongan_bpjs_kesehatan_total'] = potongan_bpjs_kesehatan_total
                satu['total_diterima'] = total_diterima
                satu['total_spp'] = total_spp

            docs[employee_id_id] = satu

        if format_report == 'direksi':
            report_name = 'berdikari.report_payslip_karyawan_direksi'
            title = 'Laporan Rekapitulasi Gaji Direksi'
        elif format_report == 'karyawan_tetap' or format_report == 'karyawan_kontrak':
            report_name = 'berdikari.report_payslip_karyawan'

            if format_report == 'karyawan_tetap':
                title = 'Laporan Rekapitulasi Gaji Karyawan Tetap'
            else:
                title = 'Laporan Rekapitulasi Gaji Karyawan Kontrak'

        elif format_report == 'penjaga':
            report_name = 'berdikari.report_payslip_penjaga'
            title = 'Laporan Rekapitulasi Gaji Penjaga'
        else:
            return Util.jek_pop1('Belum di set untuk Format Report Tersebut')

        datas = {'title': title, 'docs': docs,}
        rep = self.env.ref(report_name)
        ret = rep.with_context(landscape=True).report_action(2, data=datas)
        return ret


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'
    _description = 'Berdikari Inherit HR Payslip Line'

    account_id = fields.Many2one('account.account')
    appears_on_payslip = fields.Boolean()
    amount_python_compute = fields.Text()
    rule_parent_id = fields.Many2one('hr.salary.rule.category', related='salary_rule_id.category_id.parent_id')
    is_header = fields.Boolean(related='salary_rule_id.category_id.header', string='Header')
    order = fields.Integer(related='salary_rule_id.category_id.order', string='Order')


class HrPayslipAttendanceDays(models.Model):
    _name = 'berdikari.hr.payslip.overtime'
    _description = 'Payslip Attendance Days'
    _order = 'payslip_id, sequence'

    name = fields.Char(string='Description', required=True)
    payslip_id = fields.Many2one('hr.payslip', string='Pay Slip', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(required=True, index=True, default=99)
    overtime_date_from = fields.Datetime()
    overtime_date_to = fields.Datetime()
    overtime_day = fields.Char()
    no_of_hours = fields.Float(string='Number of Hours')
    meal_provided = fields.Boolean(string='Meal Provided by Company')
    overtime_rate = fields.Float()


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'
    _description = 'Berdikari Inherit Payslip Batches'

    period_id = fields.Many2one('berdikari.hr.attendance.period', string='Period Name')

    @api.depends('period_id')
    @api.onchange('period_id')
    def onchange_domain_seq(self):
        domain = {}
        period_id = self.period_id.id
        if period_id:
            domain_seq = [('attendance_period_id', '=', period_id)]
            domain['period_seq_id'] = domain_seq
        hasil = {'domain': domain}
        return hasil

    period_seq_id = fields.Many2one('berdikari.hr.attendance.period.line', string='Period Sequence')

    @api.depends('period_seq_id')
    @api.onchange('period_seq_id')
    def onchange_period_seq(self):
        for rec in self:
            period_seq_id = rec.period_seq_id.id
            model_period_line = self.env['berdikari.hr.attendance.period.line']
            if period_seq_id:
                period_line = model_period_line.search([('id', '=', period_seq_id)], limit=1)
                rec.date_from = period_line.date_from
                rec.date_to = period_line.date_to

    date_from = fields.Date(string='Date From', readonly=True, default=False)
    date_to = fields.Date(string='Date To', readonly=True, default=False)
