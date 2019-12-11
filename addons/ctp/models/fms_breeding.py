# -*- coding: utf-8 -*-
import io

from odoo.addons.jekdoo.utils.util import Util
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
from odoo.exceptions import ValidationError

from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

import datetime

try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

import base64


class FMSBreeding(models.Model):
    _name = 'berdikari.fms.breeding'
    _rec_name = 'number'

    number = fields.Char(string='Number', default=lambda self: self.env['ir.sequence'].next_by_code('berdikari.fms.breeding'))
    date = fields.Date()
    file_name = fields.Char()

    def default_company(self):
        return self.env.user.company_id.id

    src_company_id = fields.Many2one('res.company', string='Company', required=True, default=default_company)
    notes = fields.Text()
    fms_breeding_detail = fields.One2many('berdikari.fms.breeding.line','fms_breeding_id',string='FMS Breeding Detail')

    file1 = fields.Binary(attachment=True)
    file1_name = fields.Char()

    def _compute_fms_breeding_line2(self):
        for rec in self:
            rec.fms_breeding_line2 = rec.fms_breeding_detail
    fms_breeding_line2 = fields.One2many('berdikari.fms.breeding.line', 'fms_breeding_id', compute='_compute_fms_breeding_line2')

    def _compute_fms_breeding_line3(self):
        for rec in self:
            rec.fms_breeding_line3 = rec.fms_breeding_detail
    fms_breeding_line3 = fields.One2many('berdikari.fms.breeding.line', 'fms_breeding_id', compute='_compute_fms_breeding_line3')

    def _compute_fms_breeding_line4(self):
        for rec in self:
            rec.fms_breeding_line4 = rec.fms_breeding_detail
    fms_breeding_line4 = fields.One2many('berdikari.fms.breeding.line', 'fms_breeding_id', compute='_compute_fms_breeding_line4')

    @api.onchange('file1')
    def onchange_file1(self):
        values = {}
        if self.file1:
            import xlrd
            map1 = {
                str('Finished Goods').lower(): ['finished_goods', 'many2one', 'product.template', 'Finished Goods'],
                str('Flock').lower(): ['flock', 'many2one', 'berdikari.flock.master', 'Flock'],
                str('Chicken Coop').lower(): ['chicken_coop', 'many2one', 'berdikari.chicken.coop', 'Chicken Coop'],
                str('Date').lower(): 'date',
                str('Age (Days)').lower(): 'age',
                str('Death').lower(): 'death',
            }
            vals = []
            if not vals:
                vals = self.read_xls(map1)

            if not vals:
                vals = self.read_csv(map1)

            if vals:
                values['fms_breeding_detail'] = vals
                return {'value': values}
            else:
                print("########## NO DATA ADDED ############")

    def read_csv(self, map1):
        # import ipdb; ipdb.set_trace()

        vals = []
        if self.file1:
            import xlrd
            import base64

            file1 = base64.b64decode(self.file1).decode()

            import pandas as pd
            from pandas.compat import StringIO, BytesIO

            df = pd.read_csv(StringIO(file1))
            cols = df.columns.tolist()

            if self.fms_breeding_detail:
                for one in self.fms_breeding_detail:
                    vals.append((2, one.id))

            x = 0
            while x < len(df):
                val_one = {}
                for col in cols:
                    lower_col = str(col).lower()
                    get_map = map1.get(lower_col, '')

                    value = df[col][x]

                    if type(get_map) is list:
                        col_to_save = get_map[0]
                        if col_to_save:
                            val_to_save = False
                            tipe = get_map[1]
                            model = get_map[2]

                            if tipe == 'many2one':
                                model = self.env[model]
                                rec = model.search([('name', '=', value)])
                                if not rec:
                                    # create first
                                    # rec = model.create({'name': value})
                                    raise ValidationError(_('{} : "{}" is not known'.format(col, value)))


                                val_to_save = rec.id

                            val_one[col_to_save] = val_to_save
                    else:
                        col_to_save = get_map
                        if col_to_save:
                            val_one[col_to_save] = value

                vals.append((0, 0, val_one))
                x += 1
        return vals

    def read_xls(self, map1):
        # import ipdb; ipdb.set_trace()

        file1 = base64.b64decode(self.file1)
        try:
            book = xlrd.open_workbook(file_contents=file1 or b'')
        except:
            return []

        sheet = book.sheet_by_index(0)

        cols = []
        vals = []
        x = -1
        for row in pycompat.imap(sheet.row, range(sheet.nrows)):
            x += 1
            val_one = {}
            c = -1
            for cell in row:
                c += 1
                if x == 0:
                    col = str(cell.value).lower()
                    get_map = map1.get(col, '')
                    # if type(get_map) is list:
                    #     col_to_save = get_map[0]
                    # else:
                    #     col_to_save = get_map
                    # cols.append(col_to_save)
                    cols.append(get_map)
                else:
                    get_map = cols[c]
                    if not get_map:
                        continue

                    val = ''
                    if cell.ctype is xlrd.XL_CELL_NUMBER:
                        is_float = cell.value % 1 != 0.0
                        val = pycompat.text_type(cell.value) if is_float else pycompat.text_type(int(cell.value))
                    elif cell.ctype is xlrd.XL_CELL_DATE:
                        is_datetime = cell.value % 1 != 0.0
                        # emulate xldate_as_datetime for pre-0.9.3
                        dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(cell.value, book.datemode))
                        val = dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if is_datetime else dt.strftime(
                            DEFAULT_SERVER_DATE_FORMAT)
                    elif cell.ctype is xlrd.XL_CELL_BOOLEAN:
                        val = u'True' if cell.value else u'False'
                    elif cell.ctype is xlrd.XL_CELL_ERROR:
                        # raise ValueError(
                        #     _("Error cell found while reading XLS/XLSX file: %s") %
                        #     xlrd.error_text_from_code.get(
                        #         cell.value, "unknown error code %s" % cell.value)
                        # )
                        val = ''
                    else:
                        # import ipdb; ipdb.set_trace()
                        # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", cell)
                        val = cell.value
                    # val_one[field] = val

                    value = val
                    if type(get_map) is list:
                        col_to_save = get_map[0]
                        col = get_map[3]
                        if col_to_save:
                            val_to_save = False
                            tipe = get_map[1]
                            model = get_map[2]

                            if tipe == 'many2one':
                                model = self.env[model]
                                rec = model.search([('name', '=', value)])
                                if not rec:
                                    # create first
                                    # rec = model.create({'name': value})
                                    raise ValidationError(_('{} : "{}" is not known'.format(col, value)))

                                val_to_save = rec.id

                            val_one[col_to_save] = val_to_save
                    else:
                        col_to_save = get_map
                        if col_to_save:
                            val_one[col_to_save] = value

            if val_one:
                vals.append((0, 0, val_one))
        return vals

    @api.model
    def create(self, vals):
        rec = super(FMSBreeding, self).create(vals)
        return rec


class FMSBreedingDetail(models.Model):
    _name = 'berdikari.fms.breeding.line'
    _description = 'Berdikari FMS Breeding Line'

    fms_breeding_id = fields.Many2one('berdikari.fms.breeding')

    finished_goods = fields.Many2one('product.template')
    flock = fields.Many2one('berdikari.flock.master')
    chicken_coop = fields.Many2one('berdikari.chicken.coop')
    date = fields.Date()
    age = fields.Integer(string='Age(Days)')
    death = fields.Integer()

    by_product = fields.Char()
    male = fields.Boolean()
    female = fields.Boolean()
    feed_name = fields.Many2one('product.template')
    feed_code = fields.Char(related='feed_name.default_code')
    standard = fields.Char()
    actual = fields.Char()
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure')
    temperature = fields.Float()
    humdity = fields.Float()
    light = fields.Float()
    medicine_name = fields.Many2one('product.template')
    medicine_code = fields.Char(related='medicine_name.default_code')
    qty = fields.Float()
    med_uom_id = fields.Many2one('uom.uom', 'Medium UOM')
    vaccine_name = fields.Many2one('product.template')
    vaccine_code = fields.Char(related='vaccine_name.default_code')
    vaccine_qty = fields.Float()
    vaccine_uom_id = fields.Many2one('uom.uom', 'Vaccine UOM')
    chemical_name = fields.Many2one('product.template')
    chemical_code = fields.Char(related='chemical_name.default_code')
    chemical_qty = fields.Float()
    chemical_uom_id = fields.Many2one('uom.uom', 'Chemical UOM')
    weight = fields.Float()
    weight_uom_id = fields.Many2one('uom.uom', 'Weight UOM')
    remark = fields.Text()
    # material use tab
    manufacturing_order_id = fields.Many2one('mrp.production')
    # death tab
    biological_assets_name = fields.Many2one('product.template')
    biological_assets_code = fields.Char(related='biological_assets_name.default_code')
    biological_assets_qty = fields.Float()
    biological_assets_uom_id = fields.Many2one('uom.uom', 'Biological Assets UOM')

    def _compute_fms_breeding_line4(self):
        for rec in self:
            rec.fms_breeding_line4 = rec.berdikari_fms_breeding_line
    fms_breeding_line4 = fields.One2many('berdikari.fms.breeding.line', compute=_compute_fms_breeding_line4)