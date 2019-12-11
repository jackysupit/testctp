# -*- coding: utf-8 -*-
import os
from odoo import http, _
import datetime

# TEMPLATE_AKTIF = 'template1'
TEMPLATE_AKTIF = 'template_peruri_frontend'
PATH_TO_TEMPLATE = '/jekdoo/static/' + TEMPLATE_AKTIF
dir_path = os.path.dirname(os.path.realpath(__file__))
PATH_LAYOUT = dir_path + '/../static/' + TEMPLATE_AKTIF

class JekLog():
    @staticmethod
    def login(**kw):
        user_id = kw.get('user_id')
        expired_at = datetime.datetime.now() + datetime.timedelta(days=1)
        model_user_log = http.request.env['peruri.user_log'].sudo()

        # http.request.session['username'] = username
        return str(kw)