# -*- coding: utf-8 -*-
import os
import json
from random import randint
import random
import hashlib
from odoo import http, _
import base64
from odoo import models, fields, api, _, tools, SUPERUSER_ID

# SALTCHARS = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz1234567890"
SALTCHARS = "ShxksDcjiNVHXlWv71rm2ugBOqze0wPRMGaLCnfY93ZJpE5UoIAFy4t6bd8KQT"
delimiter = '.'


class Util():
    uid = False
    user = False
    
    def __init__(self):
        self.name = "jekdoo.util"

    @staticmethod
    def get_setup(context = None):
        if context is not None:
            setup = context.env['jekdoo.setup'].sudo()
        else:
            setup = http.request.env['jekdoo.setup'].sudo()

        rows = setup.search([], order='id desc', limit=1)
        if rows:
            row = rows[0]
        else:
            row = setup.create({})
            # raise Warning(_('setup is not set!'))

        if not row:
            raise Warning(_('create setup failed!'))
        return row

    @staticmethod
    def base64_to_file(setup, context=None):
        row = Util.get_setup(context)
        storage_directory = row.storage_directory
        storage_url = row.storage_url
        web_base_url = row.web_base_url
        base64bytes = setup['base64string']
        dest_folder = setup['dest_folder']
        dest_filename = setup['dest_filename']
        replace_exists = setup['replace_exists']

        folder_parent = storage_directory + dest_folder
        status,message = False,'Failed'

        import base64
        import os
        if not os.path.exists(folder_parent):
            if replace_exists:
                os.makedirs(folder_parent)
            else:
                status,message = False,'Destination file exists'
        dokumen_file_path = dest_folder + '/' + dest_filename
        dokumen_file_path_full = storage_directory + dokumen_file_path
        file_tujuan =  dokumen_file_path_full
        file_url = storage_url + dokumen_file_path

        if os.path.exists(file_tujuan):
            os.remove(file_tujuan)
        with open(file_tujuan, "wb") as fh:
            # fh.write(base64.decodebytes(base64bytes.encode('ascii')))
            # fh.write(base64bytes)
            fh.write(base64.b64decode(base64bytes))
            status, message = True, 'OK'

        the_result = {
            'status': status,
            'message': message,
            'folder_path': dokumen_file_path,
            'file_path': dokumen_file_path_full,
            'file_url': file_url,
        }

        return the_result

    #
    # @staticmethod
    # def api_key_check_kwargs(kwargs):
    #     msg = ""
    #     json_value = kwargs.get('json')
    #     if (not json_value):
    #         msg = "JSON value must not be empty!"
    #
    #     post = json.loads(json_value)
    #     api_key = post.get("api_key")
    #
    #     api_key_is_valid = Util.api_key_check(api_key)
    #     if(not api_key_is_valid):
    #         msg = "API Key is invalid: " + api_key
    #
    #     return api_key_is_valid,msg
    #

    # <editor-fold desc="Step To Generate A Secret Key">
    # step to generate A key
    # 1. RANDOM_NUMBER = create random number between 10 - (len(SALTCHARS) / 2)
    # 2. XPOS = RANDOM_NUMBER
    # 4. KEY_1 = RANDOM String(XPOS)
    # 5. FIRST_CHAR = SALTCHAR[XPOS]
    # 6. KEY_2 = MD5(KEY_1)
    # 7. API_KEY = FIRST_CHAR + KEY_1 + KEY_2
    # </editor-fold>
    @staticmethod
    def api_key_generate(user_id, api_code, SALT):
        if not SALT: salt = SALTCHARS
        max_number = len(SALT) - len(api_code)
        min_number = randint(5, 10)
        xpos = randint(min_number, max_number)
        firstChar = SALT[xpos:xpos+1]
        key_1 = ''.join(random.choice(SALT) for _ in range(xpos)).strip()
        key_2= hashlib.md5(key_1.encode('utf-8')).hexdigest()
        key_3 = str(base64.b64encode(api_code.encode('ascii')))

        api_key = str(user_id) + delimiter + firstChar + key_1 + key_2 + key_3
        # api_key = '12.K1C07TBVMLGFR9DYFVEC243736cce580657520a195a2e3d2141eb12.K1C07TBVMLGFR9DYFVEC243736cce580657520a195a2e3d2141eb'

        return  api_key


    # <editor-fold desc="Step To Decode A Secret Key">
    # step to Decode A key
    # 1. FIRST_CHAR = API_KEY[0]
    # 2. XPOS = SALTCHARS.indexOf(FIRST_CHAR)
    # 3. JUMLAH_RANDOM = XPOS
    # 4. KEY_1 = substr(API_KEY, 1, JUMLAH_RANDOM)
    # 4. KEY_2 = substr(API_KEY, 1 + JUMLAH_RANDOM, len(API_KEY) - (1 + JUMLAH_RANDOM))
    # 5. KEY_1_md5 = MD5(KEY_1)
    # 6. RESULT = KEY_1_md5 == KEY_2
    # </editor-fold>1
    @staticmethod
    def api_key_check(api_key, api_code, SALT):
        msg = ''

        api_key_with_user_id = api_key
        array1 = api_key_with_user_id.split(delimiter)

        if(len(array1) != 2): return False

        user_id = array1[0]
        api_key = array1[1]

        firstChar = api_key[0:1]
        xpos = SALTCHARS.find(firstChar)
        key_1 = api_key[1:xpos+1]
        len_api_key = len(api_key)
        key_2b = api_key[xpos+1:len_api_key]
        key_3 = str(base64.b64encode(api_code.encode('ascii')))
        key_2 = key_2b.replace(key_3, '')

        key_1_md5 = hashlib.md5(key_1.encode('utf-8')).hexdigest()
        is_valid = key_1_md5 == key_2

        if(is_valid):
            msg = 'key is valid'

            is_valid = Util.api_key_check_in_database(user_id, api_key)
        else:
            msg = 'key is invalid'

        return  is_valid,msg


    @staticmethod
    def api_key_check_in_database(user_id, api_key):
        # Sementara        matiin        dulu
        return True, 'Sementara API KEY di matikan'

        msg = ''
        is_valid = False

        # print("api key valid")
        logos = """CREATE TABLE IF NOT EXISTS api_key (
                            id serial primary key,
                            api_key varchar(250) NOT NULL,
                            created_at timestamp default NOW()
                        );"""
        http.request.env.cr.execute(logos)

        logos = "delete from api_key WHERE created_at < now()-'2 day'::interval;"
        http.request.env.cr.execute(logos)

        logos = """
            select * from api_key where api_key = %s 
        """
        http.request.env.cr.execute(logos, [api_key])
        # rows = http.request.env.cr.fetchall()
        row = http.request.env.cr.fetchone()

        if(row):
            msg = 'api_key sudah terpakai'
            # print("row true | berarti api_key invalid karena sudah ada di db")
            is_valid = False
        else:
            msg = 'api_key is good'
            is_valid = True
            logos = """
                insert into api_key (api_key) select %s
            """
            http.request.env.cr.execute(logos, [api_key])

            modelPartner = http.request.env['res.partner'].sudo()
            list_odoo_user_id = modelPartner.search([('user_id', '=', user_id)])
            odoo_user_id = False
            user = False
            if list_odoo_user_id:
                user = list_odoo_user_id[0]
                odoo_user_id = user.id

            if user:
                 Util.uid = odoo_user_id
                 Util.user = user

        return  is_valid,msg


    @staticmethod
    def log_write(message, *args, **kwargs):
        Util.log_me(message, *args, **kwargs)

    @staticmethod
    def info(message, *args, **kwargs):
        Util.log_me(message, *args, **kwargs)

    @staticmethod
    def log_me(message, *args, **kwargs):
        # dir_cwd = cwd = os.getcwd()
        import getpass
        username = getpass.getuser() or 'odoo'
        dir_default = '/var/log/{}'.format(username)

        if 'log_dir' in kwargs:
            log_dir = kwargs.get('log_dir')
        else:
            log_dir = dir_default

        if '%s' in message:
            message = message % args

        message = str(message)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        import datetime
        today = datetime.datetime.today().strftime('%Y%m%d')
        log_file = log_dir + '/odoo-log-{}.log'.format(today)
        open(log_file, 'a').write('\n' + message)

    @staticmethod
    def shuffle_string(str):
        chars = list(str)
        random.shuffle(chars)
        return ''.join(chars)


    @staticmethod
    def jek_pop1(message='Success', title='Message'):
        return {
            'name': title,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'jekdoo.pop1',
            'target': 'new',
            'context': {'default_name': message}
        }

    @staticmethod
    def jek_redirect_to_model(model_name = None, title='',ctx = None, help = '', domain=False):
        #Note
        #Yang memanggil def ini, harus mengggunakan @api.multi
        action = {
            'type': 'ir.actions.act_window',
            'name': title,
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': model_name,
            'target': 'self',
            'help': help,
        }
        if ctx:
            action['context'] = ctx

        if domain:
            action['domain'] = domain
        return action

    @staticmethod
    def jek_open_form(context_depreceated = False, model_name = None, id = None, ctx = None):

        #Note
        #Yang memanggil def ini, harus mengggunakan @api.multi
        if not ctx:
            ctx = {}

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': model_name,
            'res_id': id,
            'target': 'self',
            'context': ctx
        }

    @staticmethod
    def jek_redirect_to_url(url):
        #Note
        #Yang memanggil def ini, harus mengggunakan @api.multi
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }

    @staticmethod
    def jek_redirect_to_file(file_url):
        #Note
        #Yang memanggil def ini, harus mengggunakan @api.multi
        # url = 'file:////' + file_url
        url = file_url
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'self',
        }

    @staticmethod
    def mm_to_mmm(mm):
        mm = int(mm)
        result = ''
        if mm == 1:
            result = 'Jan'
        elif mm == 2:
            result = 'Feb'
        elif mm == 3:
            result = 'Mar'
        elif mm == 4:
            result = 'Apr'
        elif mm == 5:
            result = 'Mei'
        elif mm == 6:
            result = 'Jun'
        elif mm == 7:
            result = 'Jul'
        elif mm == 8:
            result = 'Agu'
        elif mm == 9:
            result = 'Sep'
        elif mm == 10:
            result = 'Okt'
        elif mm == 11:
            result = 'Nov'
        elif mm == 12:
            result = 'Des'
        return result

    @staticmethod
    def str2bool(v):
        if type (v) is bool:
            return v
        elif type (v) is str:
            return v.lower() in ("yes", "y", "true", "t", "1")
        else:
            return bool(v)

    @staticmethod
    def generate_url(model, id, field, filename_field, ctx = None, **kw):
        if ctx:
            record_config = Util.get_setup(ctx)
        else:
            record_config = Util.get_setup()

        web_base_url = record_config.web_base_url

        param_url = {
            'web_base_url': web_base_url,
            'model': model,
            'id': id,
            'field': field,
            'filename_field': filename_field,
        }
        ori_url = '{web_base_url}/download/{model}/{id}/{field}/{filename_field}'
        url = ori_url.format(**param_url)
        return url

class UtilRoutes(http.Controller):
    @http.route('/shuffle_string', methods=['GET'], auth='public', type='http', website=True, csrf=False)
    def shuffle_string(self, **kw):
        if 'str' in kw and kw.get('str'):
            str = kw.get('str')
            hasil = Util.shuffle_string(str)
        else:
            str = SALTCHARS
            hasil = Util.shuffle_string(str)
            hasil = "set query parameter 'str' untuk men-shuffle string.<br/> default menggunakan SALTCHARS:<br/>" + hasil
        return hasil

    @http.route('/api_key_gen', methods=['GET'], auth='public', type='http', website=True, csrf=False)
    def api_key_gen(self, **kw):
        user_id = kw.get('user_id') or 12
        api_code = kw.get('api_code') or 'sigmaperuri'
        salt = kw.get('salt') or SALTCHARS

        api_key = Util.api_key_generate(user_id,api_code,salt)
        return api_key


    @http.route('/api_key_check', methods=['GET'], auth='public', type='http', website=True, csrf=False)
    def api_key_check(self, **kw):
        api_key = kw.get('api_key') or None
        api_code = kw.get('api_code') or 'sigmaperuri'
        salt = kw.get('salt') or SALTCHARS

        if not api_key:
            return 'API KEY harus di isi'

        is_valid = Util.api_key_check(api_key,api_code,salt)
        hasil = 'True' if is_valid else 'False'
        return 'is_valid: ' + str(hasil)