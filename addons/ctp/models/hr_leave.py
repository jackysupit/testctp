# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class HolidayRequest(models.Model):
    _inherit = 'hr.leave'
    _description = 'Inherit HR Leave'

    @api.multi
    @api.constrains('holiday_status_id', 'date_to', 'date_from')
    def _check_leave_type_validity(self):
        print('################## test ya')
        for leave in self:
            if leave.holiday_status_id.validity_start and leave.holiday_status_id.validity_stop:
                vstart = leave.holiday_status_id.validity_start
                vstop = leave.holiday_status_id.validity_stop
                carry_cut_off_date = leave.holiday_status_id.carry_cut_off_date
                dfrom = leave.date_from
                dto = leave.date_to

                if dfrom and dto and (dfrom.date() < vstart or dto.date() > vstop):
                    if dfrom and dto and (dfrom.date() > carry_cut_off_date or dto.date() > carry_cut_off_date):
                        raise UserError(
                            _('You can take %s only between %s and %s or less than %s') % (
                                leave.holiday_status_id.display_name, leave.holiday_status_id.validity_start,
                                leave.holiday_status_id.validity_stop, leave.holiday_status_id.carry_cut_off_date))
