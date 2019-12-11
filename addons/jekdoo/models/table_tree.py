from odoo import models, fields

class View(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('jekdoo_table_tree', 'Table Tree')])

class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[('jekdoo_table_tree', 'Table Tree')])