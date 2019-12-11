# -*- coding: utf-8 -*-
from odoo import http
from . import vars
import json

route_api_check_get1 = vars.route_api_check_get1
route_api_check_post_http1 = vars.route_api_check_post_http1
route_api_check_post_json1 = vars.route_api_check_post_json1

route_api_check_get1_public = vars.route_api_check_get1_public
route_api_check_post_http1_public = vars.route_api_check_post_http1_public
route_api_check_post_json1_public = vars.route_api_check_post_json1_public

class ApiCheck(http.Controller):
    _name = 'jekdoo.api_check'

    ####----------------------------------------------------------------------------------------------------------------
    ## User
    ####----------------------------------------------------------------------------------------------------------------

    @http.route(route_api_check_get1, methods=['GET'], auth='user', type='http', website=True, csrf=False)
    def dev_route_api_check_get1(self,  **kw):
        data = {
            'status': True,
            'message': 'Hello, this is Api Check (http / user) Get 1. If you are reading this, it means you have succesfully accessing this API.',
            'parameters': {
                'notes': 'if you passed parameters, then they should appears below',
                'kw': kw,
            }
        }
        return json.dumps(data)

    @http.route(route_api_check_post_http1, methods=['POST'], auth='user', type='http', website=True, csrf=False)
    def dev_route_api_check_post_http1(self,  **kw):
        data = {
            'status': True,
            'message': 'Hello, this is Api Check (http / user) POST 1. If you are reading this, it means you have succesfully accessing this API.',
            'parameters': {
                'notes': 'if you passed parameters, then they should appears below',
                'kw': kw,
            }
        }
        return json.dumps(data)

    @http.route(route_api_check_post_json1, methods=['POST'], auth='user', type='json', website=True, csrf=False)
    def dev_route_api_check_post_json1(self,  **kw):
        data = {
            'status': True,
            'message': 'Hello, this is Api Check (json / user) POST 1. If you are reading this, it means you have succesfully accessing this API.',
            'parameters': {
                'notes': 'if you passed parameters, then they should appears below',
                'kw':kw,
            }
        }
        return json.dumps(data)

    ####----------------------------------------------------------------------------------------------------------------
    ##Public
    ####----------------------------------------------------------------------------------------------------------------

    @http.route(route_api_check_get1_public, methods=['GET'], auth='public', type='http', website=True, csrf=False)
    def dev_route_api_check_get1_public(self,  **kw):
        data = {
            'status': True,
            'message': 'Hello, this is Api Check (http / public) Get 1. If you are reading this, it means you have succesfully accessing this API.',
            'parameters': {
                'notes': 'if you passed parameters, then they should appears below',
                'kw': kw,
            }
        }
        return json.dumps(data)

    @http.route(route_api_check_post_http1_public, methods=['POST'], auth='public', type='http', website=True, csrf=False)
    def dev_route_api_check_post_http1_public(self,  **kw):
        data = {
            'status': True,
            'message': 'Hello, this is Api Check (http / public) POST 1. If you are reading this, it means you have succesfully accessing this API.',
            'parameters': {
                'notes': 'if you passed parameters, then they should appears below',
                'kw': kw,
            }
        }
        return json.dumps(data)

    @http.route(route_api_check_post_json1_public, methods=['POST'], auth='public', type='json', website=True, csrf=False)
    def dev_route_api_check_post_json1_public(self,  **kw):
        data = {
            'status': True,
            'message': 'Hello, this is Api Check (json / public) POST 1. If you are reading this, it means you have succesfully accessing this API.',
            'parameters': {
                'notes': 'if you passed parameters, then they should appears below',
                'kw':kw,
            }
        }
        return json.dumps(data)