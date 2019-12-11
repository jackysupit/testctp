# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class Batch(models.Model):
    _name = 'berdikari.wo.batch'
    _description = 'HE Batch'

    name = fields.Char(string='Name')
