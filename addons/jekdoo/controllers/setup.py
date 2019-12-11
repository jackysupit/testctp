# -*- coding: utf-8 -*-
from odoo import http, _
from odoo import SUPERUSER_ID

import json
from ..utils import jekvar

import logging
_logger = logging.getLogger(__name__)

route_jekdoo = '/jekdoo'
route_setup = route_jekdoo + '/setup'


class Setup(http.Controller):
    @http.route(route_setup + '/json', methods=['GET', 'POST'], auth='public', type='json', website=True, csrf=False)
    def post_setup_json(self):
        return self.post_setup()

    @http.route(route_setup + '/http', methods=['GET', 'POST'], auth='public', type='http', website=True, csrf=False)
    def post_setup_http(self):
        return self.post_setup()

    def post_setup(self):
        model_setup = http.request.env['jekdoo.setup'].sudo()

        fields = [
                  'min_password_length',
                  'jekdoo_max_upload_size',
                  # 'white_list_email', #kenapa ada white_list_email di sini? Buat apa? belum tau kebutuhannya, matiin dulu deh
                  'jekdoo_file_extention_allowed',
                  'web_base_url',
                  'name',
                  'max_password_length',
                  'is_user_biasa',
                  ]
        row_setup = model_setup.search_read(
            [],
            # fields=fields,
            order='id desc',
            limit=1
        )
        if not row_setup:
            row_setup = model_setup.create({})

        if row_setup:
            first_row = {}
            for fi in fields:
                first_row[fi] = getattr(row_setup, fi) if hasattr(row_setup, fi) else ''

            # first_row = row_setup[0]

            if http.request.env.user:
                user = http.request.env.user
                if user:
                    is_admin = user.id == SUPERUSER_ID
                else:
                    is_admin = False

                first_row['user_id'] = user.id
                first_row['is_user_biasa'] = user.has_group('jekdoo.read_only_user')
                first_row['is_admin'] = is_admin
                first_row['SUPERUSER_ID'] = SUPERUSER_ID

            # import ipdb; ipdb.set_trace()

            result = {
                'status': True,
                'msg': '',
                'setup': first_row,
            }
        else:
            result = {
                'status': False,
                'msg': 'Creating Custom Set Failed!',
            }

        # import ipdb;ipdb.set_trace()
        return json.dumps(result)