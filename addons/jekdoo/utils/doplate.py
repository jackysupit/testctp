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


class DoPlate(http.Controller):

    @http.route('/dodi/home', methods=['GET'], auth='public', type='http', website=True, csrf=False)
    def get_home(self, **kw):

        page_title = 'ini title'
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

    @http.route('/dodi/detail_product', methods=['GET'], auth='public', type='http', website=True, csrf=False)
    def get_detail_product(self, **kw):

        page_title = 'Detail Product'
        page_description = 'ini description'
        page_keywords = 'ini keywords'
        product_title = 'e-Materai'

        kw['page_title'] = page_title
        kw['page_description'] = page_description
        kw['page_keywords'] = page_keywords
        kw['product_title'] = product_title
        kw['html_file_name'] = '/content/produk_detail.html'

        header = JekPlate.get_header(**kw)
        content = JekPlate.get_content(**kw)
        footer = JekPlate.get_footer(**kw)

        home = header + content + footer
        return home

    @http.route('/dodi/pesan', methods=['GET'], auth='public', type='http', website=True, csrf=False)
    def get_order(self, **kw):

        page_title = 'Pesan Produk'
        page_description = 'ini description'
        page_keywords = 'ini keywords'
        product_title = 'e-Materai'

        kw['page_title'] = page_title
        kw['page_description'] = page_description
        kw['page_keywords'] = page_keywords
        kw['product_title'] = product_title
        kw['html_file_name'] = '/content/pesan.html'

        header = JekPlate.get_header(**kw)
        content = JekPlate.get_content(**kw)
        footer = JekPlate.get_footer(**kw)

        home = header + content + footer
        return home