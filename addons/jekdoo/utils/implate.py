# -*- coding: utf-8 -*-
import os
import json
from random import randint
import random
import hashlib
from odoo import http
import base64
from .jekplate import JekPlate 

# TEMPLATE_AKTIF = 'template1'
TEMPLATE_AKTIF = 'template_peruri_frontend'
PATH_TO_TEMPLATE = '/jekdoo/static/' + TEMPLATE_AKTIF
dir_path = os.path.dirname(os.path.realpath(__file__))
PATH_LAYOUT = dir_path + '/../static/' + TEMPLATE_AKTIF


class JekPlateTest(http.Controller):

    @http.route('/imer/home', methods=['GET'], auth='public', type='http', website=True, csrf=False)
    def get_home(self, **kw):
        html_file_name_header = '/layout/header.html'
        html_file_name_footer = '/layout/footer.html'

        html_file_name_home = '/content/home.html'

        page_title = 'Peruri | Digital Touch Point'
        page_description = 'ini description'
        page_keywords = 'ini keywords'
        product_title = 'e-Materai'

        kw['page_title'] = page_title
        kw['page_description'] = page_description
        kw['page_keywords'] = page_keywords
        kw['product_title'] = product_title
        kw['html_file_name'] = '/content/home.html'

        header = JekPlate.get_header(**kw)
        content = JekPlate.get_content(**kw)
        footer = JekPlate.get_footer(**kw)

        home = header + content + footer
        return home

    @http.route('/imer/login', methods=['GET'], auth='public', type='http', website=True, csrf=False)
    def get_login(self, **kw):
        html_file_name_header = '/layout/header.html'
        html_file_name_footer = '/layout/footer.html'

        html_file_name_home = '/content/login.html'

        page_title = 'Login'
        page_description = 'ini description'
        page_keywords = 'ini keywords'
        product_title = 'e-Materai'

        kw['page_title'] = page_title
        kw['page_description'] = page_description
        kw['page_keywords'] = page_keywords
        kw['product_title'] = product_title
        kw['html_file_name'] = '/content/login.html'
        kw['label_search'] = 'search'

        header = JekPlate.get_header(**kw)
        content = JekPlate.get_content(**kw)
        footer = JekPlate.get_footer(**kw)

        home = header + content + footer
        return home

    @http.route('/imer/register', methods=['GET'], auth='public', type='http', website=True, csrf=False)
    def get_register(self, **kw):
        html_file_name_header = '/layout/header.html'
        html_file_name_footer = '/layout/footer.html'

        html_file_name_home = '/content/register.html'

        page_title = 'Register'
        page_description = 'ini description'
        page_keywords = 'ini keywords'
        product_title = 'e-Materai'

        kw['page_title'] = page_title
        kw['page_description'] = page_description
        kw['page_keywords'] = page_keywords
        kw['product_title'] = product_title
        kw['html_file_name'] = '/content/register.html'
        kw['label_search'] = 'search'

        header = JekPlate.get_header(**kw)
        content = JekPlate.get_content(**kw)
        footer = JekPlate.get_footer(**kw)

        home = header + content + footer
        return home

    @http.route('/imer/produk', methods=['GET'], auth='public', type='http', website=True, csrf=False)
    def get_produk(self, **kw):
        html_file_name_header = '/layout/header.html'
        html_file_name_footer = '/layout/footer.html'

        html_file_name_home = '/content/produk.html'

        page_title = 'Katalog Produk'
        page_description = 'ini description'
        page_keywords = 'ini keywords'
        product_title = 'Katalog Produk'

        kw['page_title'] = page_title
        kw['page_description'] = page_description
        kw['page_keywords'] = page_keywords
        kw['product_title'] = product_title
        kw['html_file_name'] = '/content/produk.html'
        kw['label_search'] = 'search'

        header = JekPlate.get_header(**kw)
        content = JekPlate.get_content(**kw)
        footer = JekPlate.get_footer(**kw)

        home = header + content + footer
        return home