# -*- coding: utf-8 -*-
from odoo.osv import expression
# from odoo.addons.web.controllers.main import clean_action
from odoo.tools.safe_eval import safe_eval

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.jekdoo.utils.util import Util

from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class AccountReport(models.AbstractModel):
    _inherit = 'account.financial.html.report'
    # _inherit = 'account.report'
    _description = 'Account Report'

    filter_operating_unit = None
    operating_unit = fields.Boolean('Operating Unit option')

    def get_operating_unit(self, options, previous_options = False):
        selected_operating_unit_ids = {}
        if previous_options:
            if previous_options.get('operating_unit'):
                selected_operating_unit_ids = [j.get('id') for j in previous_options.get('operating_unit') if j.get('selected')]

        company_id = self.env.user.company_id
        records_operating_unit_ids = self.env['operating.unit'].search([('company_id','=',company_id.id)])

        operating_unit_ids = []
        previous_unit = False
        for unit in records_operating_unit_ids:
            if previous_unit and unit.id != previous_unit:
                operating_unit_ids.append({'id': 'divider', 'name': unit.name})

            previous_unit = unit.id
            operating_unit_ids.append({'id': unit.id, 'code': unit.code, 'name': unit.name, 'selected': unit.id in selected_operating_unit_ids})
        return operating_unit_ids

    def _build_options(self, previous_options=None):
        options = super(AccountReport, self)._build_options(previous_options)
        options['operating_unit'] = self.get_operating_unit(options, previous_options)
        return options
