# -*- coding: utf-8 -*-
import os
import json
from random import randint
import random
import hashlib
from odoo import http, _
import base64
from . import util
from pathlib import Path
import datetime, time


Util = util.Util

class JekPlate():

    def __init__(self):
        self.name = "jekdoo.jekplate"

    @staticmethod
    def open_file(file_path):
        file_header = open(file_path, 'r')
        isi_file = file_header.read()
        return isi_file

    @staticmethod
    def get_header(**kw):
        kw['html_file_name'] = '/layout/head.html'
        head = JekPlate.get_content(**kw)

        kw['html_file_name'] = '/layout/header.html'
        header = JekPlate.get_content(**kw)

        content = head + header
        return content

    @staticmethod
    def get_header_detail(**kw):
        kw['html_file_name'] = '/layout/head.html'
        head = JekPlate.get_content(**kw)

        kw['html_file_name'] = '/layout/header_detail.html'
        header = JekPlate.get_content(**kw)

        content = head + header
        return content

    @staticmethod
    def get_body(**kw):
        header = JekPlate.get_header(**kw)
        footer = JekPlate.get_footer(**kw)
        content = JekPlate.get_content(**kw)
        all = header + content + footer
        return all

    @staticmethod
    def get_footer(**kw):
        kw['html_file_name'] = '/layout/footer.html'
        return JekPlate.get_content(**kw)

    @staticmethod
    def get_content(**kw):
        TEMPLATE_AKTIF = kw.get('TEMPLATE_AKTIF') or 'blank_template' 
        URL_TO_TEMPLATE = kw.get('URL_TO_TEMPLATE') or '/jekdoo/static/' + TEMPLATE_AKTIF
        dir_path = os.path.dirname(os.path.realpath(__file__))
        PATH_LAYOUT = kw.get('PATH_LAYOUT') or dir_path + '/../static/' + TEMPLATE_AKTIF

        # model_config = 'ir.config_parameter'
        # models = http.request.env[model_config].sudo()
        # row = models.search([('key', '=', 'web.base.url')])
        # if row:
        #     HOST_URL = row.value
        row_setup = Util.get_row_setup()
        HOST_URL = row_setup.web_base_url
        if not HOST_URL:
            return Warning(_('Web Base URL is not set in Setup'))
        kw['SITE_URL'] = HOST_URL

        random_int = randint(1, 10000000)
        kw['random_int'] = random_int

        datetime_now = datetime.datetime.now()
        current_mmmm_yyyy = datetime_now.strftime('%B %Y')
        kw['current_mmmm_yyyy'] = current_mmmm_yyyy

        customer_name = ''
        if 'customer_name' in http.request.session:
            customer_name = http.request.session['customer_name']

        btn_login = '<a id="btn-login-top" class="book-btn" href="/com/login">Login</a>'
        btn_logout = '<a id="btn-logout-top" class="book-btn truncate" href="/com/logout">'+customer_name+' - Logout</a>'
        if customer_name:
            btn_dipakai = btn_logout
        else:
            btn_dipakai = btn_login
        kw['button_login'] = btn_dipakai

        js_files = kw.get('js_files') or '<!-- no custom js file -->' #ini untuk memastikan, key ini selalu ada
        kw['js_files'] = js_files #ini untuk memastikan, key ini selalu ada

        kw['template_path'] = kw.get('template_path') or URL_TO_TEMPLATE
        html_file_name = kw.get('html_file_name')
        if html_file_name:
            my_file = Path(html_file_name)
            # if my_file.is_file():
            #     # file exists
            # if my_file.is_dir():
            #     # directory exists
            if my_file.exists():
                # path exists
                file_path = html_file_name
            else:
                file_path = PATH_LAYOUT + html_file_name
                
            isi_file = JekPlate.open_file(file_path)
            isi_file = isi_file.format(**kw)
        else:
            isi_file = 'html_file_name is empty'
            raise Warning(isi_file)

        return isi_file