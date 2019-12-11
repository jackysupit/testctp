# -*- coding: utf-8 -*-
"""
    - created by jeksu -
requirements:
    pip3 install xlwt #tapi sudah jadi requirementnya odoo juga, jadi ga perlu install lagi harusnya
"""

from odoo import http
from odoo.tools.misc import xlwt

class JekXLS():
    default_font_color = 'black'
    default_bg_color = 'white'

    def __init__(self, default_font_color = 'black', default_bg_color = 'white'):
        self.default_font_color = default_font_color
        self.default_bg_color = default_bg_color

    def set_color(self, default_font_color, default_bg_color):
        self.default_font_color = default_font_color
        self.default_bg_color = default_bg_color

    str_style_header_title = "font: colour {font_color}, bold on, height {font_height_18}; pattern: pattern solid, fore_colour {bg_color};align: wrap on, vert center, horiz center;"
    str_style_header_title_red = "font: colour {font_color}, bold on, height {font_height_18}; pattern: pattern solid, fore_colour red;align: wrap on, vert center, horiz center;"
    str_style_header_subtitle = "font: colour {font_color}, bold on, height {font_height_16}; pattern: pattern solid, fore_colour {bg_color};align: wrap on, vert center, horiz center;"
    str_style_header_subtitle_red = "font: colour {font_color}, bold on, height {font_height_16}; pattern: pattern solid, fore_colour red;align: wrap on, vert center, horiz center;"
    str_style_16 = "font: colour {font_color}, bold on, height {font_height_16}; pattern: pattern solid, fore_colour {bg_color};align: wrap on, vert center, horiz center;"
    str_style_16_number = "font: colour {font_color}, bold on, height {font_height_16}; pattern: pattern solid, fore_colour {bg_color};align: wrap on, vert center, horiz center;"
    str_style_16_decimal = "font: colour {font_color}, bold on, height {font_height_16}; pattern: pattern solid, fore_colour {bg_color};align: wrap on, vert center, horiz center;"
    str_style_16_red = "font: colour {font_color}, bold on, height {font_height_16}; pattern: pattern solid, fore_colour red;align: wrap on, vert center, horiz center;"
    str_style_16_red_number = "font: colour {font_color}, bold on, height {font_height_16}; pattern: pattern solid, fore_colour red;align: wrap on, vert center, horiz center;"
    str_style_16_red_decimal = "font: colour {font_color}, bold on, height {font_height_16}; pattern: pattern solid, fore_colour red;align: wrap on, vert center, horiz center;"
    str_style_14 = "font: colour {font_color}, bold on, height {font_height_14}; pattern: pattern solid, fore_colour {bg_color};align: wrap on, vert center, horiz center;"
    str_style_14_number = "font: colour {font_color}, bold on, height {font_height_14}; pattern: pattern solid, fore_colour {bg_color};align: wrap on, vert center, horiz center;"
    str_style_14_decimal = "font: colour {font_color}, bold on, height {font_height_14}; pattern: pattern solid, fore_colour {bg_color};align: wrap on, vert center, horiz center;"
    str_style_14_red = "font: colour {font_color}, bold on, height {font_height_14}; pattern: pattern solid, fore_colour red;align: wrap on, vert center, horiz center;"
    str_style_14_red_number = "font: colour {font_color}, bold on, height {font_height_14}; pattern: pattern solid, fore_colour red;align: wrap on, vert center, horiz center;"
    str_style_14_red_decimal = "font: colour {font_color}, bold on, height {font_height_14}; pattern: pattern solid, fore_colour red;align: wrap on, vert center, horiz center;"
    str_style_header_bold = "font: colour {font_color}, bold on; pattern: pattern solid, fore_colour {bg_color};"
    str_style_header_bold_right = "font: colour {font_color}, bold on; pattern: pattern solid, fore_colour {bg_color};align: wrap on, vert top, horiz right;"
    str_style_header_bold_number = "font: colour {font_color}, bold on; pattern: pattern solid, fore_colour {bg_color};align: wrap on, vert top, horiz right;"
    str_style_header_bold_decimal = "font: colour {font_color}, bold on; pattern: pattern solid, fore_colour {bg_color};align: wrap on, vert top, horiz right;"
    str_style_header_plain = "font: colour {font_color}, bold on;pattern: pattern solid, fore_colour {bg_color};"

    str_style_body = "font: colour {font_color}, bold off;align: wrap on, vert top, horiz left;"
    str_style_body_red = "font: colour {font_color}, bold off;pattern: pattern solid, fore_colour red;align: wrap on, vert top, horiz left;"
    str_style_body_red_number = "font: colour {font_color}, bold off;pattern: pattern solid, fore_colour red;align: wrap on, vert top, horiz left;"
    str_style_body_red_decimal = "font: colour {font_color}, bold off;pattern: pattern solid, fore_colour red;align: wrap on, vert top, horiz left;"
    str_style_body_right = "font: colour {font_color}, bold off;align: wrap on, vert top, horiz right;pattern: pattern solid, fore_colour {bg_color};"
    str_style_body_number = "font: colour {font_color}, bold off;align: wrap on, vert top, horiz right;pattern: pattern solid, fore_colour {bg_color};"
    str_style_body_decimal = "font: colour {font_color}, bold off;align: wrap on, vert top, horiz right;pattern: pattern solid, fore_colour {bg_color};"

    style_header_title = 'str_style_header_title'
    style_header_title_red = 'str_style_header_title_red'
    style_header_subtitle = 'str_style_header_subtitle'
    style_header_subtitle_red = 'str_style_header_subtitle_red'
    style_16 = 'str_style_16'
    style_16_number = 'str_style_16_number'
    style_16_decimal = 'str_style_16_decimal'
    style_16_red = 'str_style_16_red'
    style_16_red_number = 'str_style_16_red_number'
    style_16_red_decimal = 'str_style_16_red_decimal'
    style_14 = 'str_style_14'
    style_14_number = 'str_style_14_number'
    style_14_decimal = 'str_style_14_decimal'
    style_14_red = 'str_style_14_red'
    style_14_red_number = 'str_style_14_red_number'
    style_14_red_decimal = 'str_style_14_red_decimal'
    style_header_bold = 'str_style_header_bold'
    style_header_bold_right = 'str_style_header_bold_right'
    style_header_bold_number = 'str_style_header_bold_number'
    style_header_bold_decimal = 'str_style_header_bold_decimal'
    style_header_plain = 'str_style_header_plain'
    style_body = 'str_style_body'
    style_body_red = 'str_style_body_red'
    style_body_red_number = 'str_style_body_red_number'
    style_body_red_decimal = 'str_style_body_red_decimal'
    style_body_right = 'str_style_body_right'
    style_body_number = 'str_style_body_number'
    style_body_decimal = 'str_style_body_decimal'


    #call: xls.get_style(xls.style_header_bold)
    def get_style(self, style = 'style', font_color='', num_format_str='', **kw):
        result = xlwt.easyxf()

        font_height_20 = 20 * 20  # size 20pt
        font_height_18 = 20 * 18  # size 18pt
        font_height_16 = 20 * 16  # size 16pt
        font_height_14 = 20 * 14  # size 14pt
        format_number = '_(#,##0_);(#,##0)'
        format_decimal = '_(#,##0.00_);[Red](#,##0.00)'

        param_style = {
            'font_color': self.default_font_color,
            'bg_color': self.default_bg_color,
            'font_height_20': font_height_20,
            'font_height_18': font_height_18,
            'font_height_16': font_height_16,
            'font_height_14': font_height_14,
        }

        if hasattr(self, style):
            a_style = getattr(self, style)

            param_style = param_style
            my_param_style = {}
            for akey in param_style:
                if akey == 'font_color':
                    avalue = font_color if font_color else param_style.get(akey)
                else:
                    avalue = param_style.get(akey)

                my_param_style[akey] = avalue

            new_str = a_style.format(**my_param_style)
            new_str += 'borders: top_color gray80, bottom_color gray80, right_color gray80, left_color gray80,\
                            left thin, right thin, top thin, bottom thin;'

            # print("#####################################################################################################")
            # print("#####################################################################################################")
            # print("#####################################################################################################")
            # print("style: ", style)
            # print("new_str: ", new_str)
            # print("param_style: ", my_param_style)

            if num_format_str:
                result = xlwt.easyxf(new_str, num_format_str=num_format_str)
            else:
                if style.endswith('_number'):
                    result = xlwt.easyxf(new_str, num_format_str=format_number)
                elif style.endswith('_decimal'):
                    result = xlwt.easyxf(new_str, num_format_str=format_decimal)
                else:
                    result = xlwt.easyxf(new_str)

        return result

    def new_workbook(self):
        workbook = xlwt.Workbook()
        return workbook

    def download_workbook(self, workbook, output_filename):
        response = http.request.make_response(None,
                 headers=[('Content-Type', 'application/vnd.ms-excel'),
                          ('Content-Disposition', 'attachment; filename={output_filename};'.format(
                              output_filename=output_filename))],
                 )
        workbook.save(response.stream)
        return response

    # def download_xls_data(rows_sheet, output_filename):
    #     """
    #     rows_sheet = [
    #         {
    #             'sheet_title':'sheet_title',
    #             'sheet_data': {
    #                 'header': header,
    #                 'rows_model': rows_model,
    #                 'footer': footer,
    #             }
    #         },
    #         {
    #             'sheet_title':'Feb 2019',
    #             'sheet_data': {
    #                 'header': header,
    #                 'rows_model': rows_model,
    #                 'footer': footer,
    #             }
    #         },
    #     ]
    #     """
    #
    #     workbook = xlwt.Workbook()
    #     for one_sheet in rows_sheet:
    #         sheet_title = one_sheet.get('sheet_title')
    #         sheet_data = one_sheet.get('sheet_data')
    #         """
    #             data = {
    #                 'header': header,
    #                 'rows_model': rows_model,
    #                 'footer': footer,
    #             }
    #         """
    #
    #         data_header = sheet_data.get('header')
    #         """
    #         data_header = [
    #             {
    #                 'string':'string',
    #                 'style_header':'style_header',
    #                 'style_body':'style_body',
    #                 'body_limit_char': int, width limit of the character in a line. ie: 30
    #                 },
    #             {
    #                 'string':'No',
    #                 'style_header':'font: bold on; pattern: pattern solid, vert top, fore_colour gray25;',
    #                 'style_body':'align: wrap on, vert top, horiz left'
    #                 },
    #             {
    #                 'string':'Name',
    #                 'style_header':'font: bold on; pattern: pattern solid, vert top, fore_colour gray25;',
    #                 'style_body':'align: wrap on, vert top, horiz left',
    #                 'body_limit_char':40
    #                 },
    #             {
    #                 'string':'Qty',
    #                 'style_header':'font: bold on; pattern: pattern solid, vert top, fore_colour gray25;',
    #                 'style_body':'align: wrap on, vert top, horiz right'
    #                 },
    #             {
    #                 'string':'Price',
    #                 'style_header':'font: bold on; pattern: pattern solid, vert top, fore_colour gray25;',
    #                 'style_body':'align: wrap on, vert top, horiz right'
    #                 },
    #             {
    #                 'string':'Sub Total',
    #                 'style_header':'font: bold on; pattern: pattern solid, vert top, fore_colour gray25;',
    #                 'style_body':'align: wrap on, vert top, horiz right'
    #                 },
    #         ]
    #         """
    #
    #         body_rows = sheet_data.get('body_rows')
    #         """
    #         rows_model = [
    #             (value0, value1, value2, value3, value4),
    #             (1, 'Apel', 1, 1000, 1000),
    #             (2, 'Jeruk', 3, 3000, 9000),
    #             (3, 'Mangga', 6, 4000, 24000),
    #         ]
    #         """
    #
    #         footer = sheet_data.get('footer')
    #         """
    #         footer = [
    #             ('', 'Total', '', '', 34000),
    #         ]
    #         """
    #         WS = workbook.add_sheet(sheet_title)
    #         style_header_bold = xlwt.easyxf("font: bold on; pattern: pattern solid, fore_colour gray25;")
    #         style_header_plain = xlwt.easyxf("pattern: pattern solid, fore_colour gray25;")
    #         style_body = xlwt.easyxf("align: wrap on, vert top, horiz left")
    #         style_bold = xlwt.easyxf("font: bold on;")
    #
    #         style_auto_height = xlwt.XFStyle()
    #         al = xlwt.Alignment()
    #         al.wrap = xlwt.Alignment.WRAP_AT_RIGHT
    #         style_auto_height.alignment = al
    #
    #         list_body_field = []
    #         list_body_style = []
    #         list_footer_style = []
    #         list_body_limit_char = []
    #
    #         key_header_field = 'field'
    #         key_header_string = 'string'
    #         key_header_style_header = 'style_header'
    #         key_header_style_body = 'style_body'
    #         key_header_style_footer = 'style_footer'
    #         key_header_body_limit_char = 'body_limit_char'
    #
    #         x_row_index = 0
    #         x_col_index = -1
    #         for one in data_header:
    #             x_col_index += 1
    #
    #             header_field = one.get(key_header_field)
    #             header_string = one.get(key_header_string)
    #             header_style_header = one.get(key_header_style_header)
    #             header_style_body = one.get(key_header_style_body)
    #             header_style_footer = one.get(key_header_style_footer)
    #             header_body_limit_char = one.get(key_header_body_limit_char)
    #
    #             list_body_field.append(header_field)
    #             list_body_style.append(header_style_body)
    #             list_footer_style.append(header_style_footer)
    #             list_body_limit_char.append(header_body_limit_char)
    #
    #             WS.write(x_row_index, x_col_index, header_string, header_style_header)
    #
    #         x_no = 0
    #         for row in body_rows:
    #             x_no += 1
    #             x_row_index += 1
    #
    #             x_col_index = -1
    #             for field_name in list_body_field:
    #                 cell_value = row.get(field_name)
    #
    #                 x_col_index += 1
    #                 style_body = list_body_style[x_col_index]
    #                 WS.write(x_row_index, x_col_index, cell_value, style_body)
    #
    #                 limit_character = list_body_limit_char[x_col_index]
    #
    #                 if limit_character:
    #                     character_width = 367
    #                     current_width = WS.col(x_col_index).width
    #                     character_count = len(cell_value)
    #                     # print("##############################################################################")
    #                     # print("##############################################################################")
    #                     # WS.write(x_row_index, column_name + 1, character_count)
    #                     # WS.write(x_row_index, column_name + 2, limit_character)
    #                     # print("characteR_count: {} | limit_character= {}".format(character_count, limit_character,))
    #                     if character_count > limit_character:
    #                         ok_character_count = limit_character
    #                     else:
    #                         ok_character_count = character_count
    #
    #                     new_width = ok_character_count * character_width
    #                     limit_width = 65536 - 1
    #                     if new_width > limit_width:
    #                         new_width = limit_width
    #                     if new_width > current_width:
    #                         WS.col(x_col_index).width = new_width
    #
    #         x_no = 0
    #         for row in footer:
    #             x_no += 1
    #             x_row_index += 1
    #
    #             x_col_index = -1
    #             for cell_value in row:
    #                 x_col_index += 1
    #                 style_footer = list_footer_style[x_col_index]
    #                 WS.write(x_row_index, x_col_index, cell_value, style_footer)
    #
    #                 limit_character = list_body_limit_char[x_col_index]
    #
    #                 if limit_character:
    #                     character_width = 367
    #                     current_width = WS.col(x_col_index).width
    #                     character_count = len(cell_value)
    #                     # print("##############################################################################")
    #                     # print("##############################################################################")
    #                     # WS.write(x_row_index, column_name + 1, character_count)
    #                     # WS.write(x_row_index, column_name + 2, limit_character)
    #                     # print("characteR_count: {} | limit_character= {}".format(character_count, limit_character,))
    #                     if character_count > limit_character:
    #                         ok_character_count = limit_character
    #                     else:
    #                         ok_character_count = character_count
    #
    #                     new_width = ok_character_count * character_width
    #                     limit_width = 65536 - 1
    #                     if new_width > limit_width:
    #                         new_width = limit_width
    #                     if new_width > current_width:
    #                         WS.col(x_col_index).width = new_width
    #
    #     return download_xls_workbook(workbook, output_filename)
