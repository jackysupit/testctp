# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.jekdoo.utils.util import Util
from odoo.exceptions import ValidationError, UserError

# from datetime import datetime

import datetime
import logging
_logger = logging.getLogger(__name__)

class AccountAccount(models.Model):
    _inherit = 'account.account'

    code_existing = fields.Char(string='Existing Code')
    name_id = fields.Char(string='Bahasa Indonesia')