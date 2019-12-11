# -*- coding: utf-8 -*-
from odoo import http
from . import vars
import json

# nama_model_view = 'ir.ui.view'
# route_set_dynamic_list = '/jekdoo/set_dynamic_list'
# route_apply2 = '/jekdoo/apply2'

nama_model_view = vars.nama_model_view
route_set_dynamic_list = vars.route_set_dynamic_list
route_apply2 = vars.route_apply2

class DynamicList(http.Controller):
    _name = 'jekdoo.dynamic_list'

    @http.route(route_apply2, methods=['POST'], auth='public', type='json', website=True, csrf=False)
    def def_apply2(self):
        return "this is from apply2"

    @http.route(route_set_dynamic_list, methods=['POST'], auth='public', type='http', website=True, csrf=False)
    def def_set_dynamic_list(self, **kw):
        model_name = kw.get('model')
        columns = json.loads(kw.get('columns'))

        model_view = http.request.env[nama_model_view]
        my_view = model_view.search(
            [
                ('model','=',model_name),
                ('type','=','tree'),
            ],
            order='priority, create_date'
        )

        the_fields = ''
        for one in columns:
            one = one.strip()
            the_fields += '\n<field name="{field_name}"/>'.format(field_name=one)

        param_arch_base = {
            'the_fields': the_fields
        }
        arch_base = """<?xml version="1.0"?>
                        <tree>
                            {the_fields}
                        </tree>
                    """.format(**param_arch_base)
        if my_view:
            my_view = my_view[0]
            status = my_view.write({"arch_base": arch_base})
        else:
            vals_to_view = {
                "priority": 16,
                "active": True,
                "mode": "primary",
                "name": model_name + '_view_tree',
                "type": "tree",
                "model": model_name,
                "field_parent": False,
                "inherit_id": False,
                "arch_base": arch_base,
                "groups_id": [[6,False,[]]]
              }
            my_view.create(vals_to_view)
            status = True

        json_hasil = {
            'status': status,
            'msg': 'set_dynamic_list!',
        }
        return json.dumps(json_hasil)