# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class JekPop(models.TransientModel):
    _name = 'jekdoo.pop1'
    name = fields.Text('Message')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(JekPop, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                  submenu=submenu)
        if view_type == 'form':
            res['arch'] = """
                <form string="Form Custom Model">
                    <field name="name" readonly="1"/>   

                    <footer>
                       <button string="Close" class="btn-default" special="cancel"/>
                    </footer>
                </form>
            """
        #   raise
        from lxml import etree
        doc = etree.XML(res['arch'])
        View = self.env['ir.ui.view'].sudo()
        res['arch'], res['fields'] = View.postprocess_and_fields(self._name, doc, view_id)
        return res
