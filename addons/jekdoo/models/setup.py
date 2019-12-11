# -*- coding: utf-8 -*-

from odoo import models, fields, api, http, _
from odoo.exceptions import ValidationError
import random
import datetime
from odoo.addons.jekdoo.utils.util import Util

import logging
_logger = logging.getLogger(__name__)

default_web_base_url = 'http://localhost:8069'
placeholder_web_base_url = default_web_base_url

default_name = 'Berdikari App'
default_jekdoo_max_upload_size = 25
default_jekdoo_file_extention_allowed = 'doc, docx, xls, xlsx, pdf, jpg, png'
default_min_password_length = 5
default_max_password_length = 10

class CustomSet(models.Model):
    _name = 'jekdoo.setup'

    name = fields.Char(string='Title', default=default_name)

    jekdoo_max_upload_size = fields.Integer(string='Max Upload Size (Mb)', default=default_jekdoo_max_upload_size)
    jekdoo_file_extention_allowed = fields.Char(string='Allowed File Extention in Lead', default=default_jekdoo_file_extention_allowed)

    def def_default_web_base_url(self):
        config_parameter = self.env['ir.config_parameter'].sudo()
        default_value = config_parameter.get_param('jekdoo.setup.web_base_url') or config_parameter.get_param('jekdoo.custom_set.web_base_url')
        if not default_value:
            default_value = config_parameter.get_param('web.base.url') or default_web_base_url
        return default_value
    web_base_url = fields.Char(string='Web Base URL', default= def_default_web_base_url, placeholder= placeholder_web_base_url, required=True)

    def _default_white_list_email(self):
        default = []
        row_setup = self.sudo().search([], limit=1, order="id desc")
        if row_setup:
            white_list_email = row_setup.white_list_email
            default = [[6, 0, [one.id for one in white_list_email]]]
        return default

    white_list_email = fields.Many2many('res.users', 'jekdoo_custom_white_list_email_rel', 'custom_id', 'user_id', string='White List Email', help="Allowed Outgoing Emails",
            default=_default_white_list_email)

    default_min_password_length = 5
    min_password_length = fields.Integer(string='Min Password Length', default=default_min_password_length)
    default_max_password_length = 10
    max_password_length = fields.Integer(string='Max Password Length', default=default_max_password_length)

    @api.model
    def create(self, vals):
        config_parameter = self.env['ir.config_parameter'].sudo()
        all_self = self.search([])
        for one in all_self:
            one.unlink()

        if 'min_password_length' in vals or 'min_password_length' in vals:
            min_password_length = vals.get('min_password_length') or 0
            min_password_length = int(min_password_length)
            max_password_length = vals.get('max_password_length') or 0
            max_password_length = int(max_password_length)

            msg = ''

            if not min_password_length or not max_password_length:
                msg = _('Min / Max Password Length must be bigger than 0')
            elif max_password_length < min_password_length:
                msg = _('Max Password Length must be bigger than Min Password Length')

            if msg:
                raise ValidationError(msg)

        parent_result = super(CustomSet, self).create(vals)

        config_parameter.set_param('jekdoo.setup.name', parent_result.name or default_name)
        config_parameter.set_param('jekdoo.setup.web_base_url', parent_result.web_base_url)
        config_parameter.set_param('jekdoo.setup.jekdoo_max_upload_size', parent_result.jekdoo_max_upload_size or default_jekdoo_max_upload_size)
        config_parameter.set_param('jekdoo.setup.jekdoo_file_extention_allowed', parent_result.jekdoo_file_extention_allowed or default_jekdoo_file_extention_allowed)
        config_parameter.set_param('jekdoo.setup.min_password_length', parent_result.min_password_length)
        config_parameter.set_param('jekdoo.setup.max_password_length', parent_result.max_password_length)

        return parent_result

    @api.multi
    def write(self, vals):
        config_parameter = self.env['ir.config_parameter'].sudo()
        result = super(CustomSet, self).write(vals)

        for rec in self:
            parent_result = rec
            config_parameter.set_param('jekdoo.setup.name', parent_result.name)
            config_parameter.set_param('jekdoo.setup.web_base_url', parent_result.web_base_url)
            config_parameter.set_param('jekdoo.setup.jekdoo_max_upload_size', parent_result.jekdoo_max_upload_size)
            config_parameter.set_param('jekdoo.setup.jekdoo_file_extention_allowed', parent_result.jekdoo_file_extention_allowed)
            config_parameter.set_param('jekdoo.setup.min_password_length', parent_result.min_password_length)
            config_parameter.set_param('jekdoo.setup.max_password_length', parent_result.max_password_length)

        return result

    @api.multi
    def action_backup_log(self):
        msg = self.backup_log()
        return Util.jek_pop1(msg)

    def backup_log(self):
        msg_all = 'Done'
        import os
        #region BACKUP CURRENT DAY
        from odoo.tools import config
        import datetime
        today = datetime.datetime.today().strftime('%Y%m%d')
        old_file = config.get('logfile')

        if old_file:
            list_file_name = old_file.split('/')
            if len(list_file_name) > 1:
                old_file_name = list_file_name[len(list_file_name)-1]
                old_dir = old_file[:(len(old_file)-len(old_file_name)-1)] #1 = back slash terakhir
            else:
                old_file_name = old_file
                old_dir = '.'
        else:
            old_file_name = 'odoo-server.log'

            import getpass
            username = getpass.getuser() or 'odoo'
            old_dir = '/var/log/{}'.format(username)
            old_file = "{}/{}".format(old_dir, old_file_name)

        use_dir = old_dir

        new_file_name = "{}-{}".format(old_file_name,today)
        new_file = os.path.join(use_dir, new_file_name)
        exists_new = os.path.isfile(new_file)
        exists_old = os.path.isfile(old_file)
        if exists_old:
            if not exists_new: #jika new sudah ada, gak perlu log lagi. biar masuk ke hari besok aja
                os.rename(old_file, new_file)
                msg = "###Backup LOG! {}".format(new_file)
            else:
                msg = "###Backup LOG Skipped! new file already exists: {}".format(new_file)
        else:
            msg = "###Backup LOG Skipped! old file does not exist: {}".format(old_file)
        msg_all += '\r\n'
        msg_all += msg
        _logger.info(msg)

        #endregion

        #region DELETE LOG > 7 DAYS
        import time
        current_time = time.time()
        for f in os.listdir(path=use_dir):
            full_f = '{}/{}'.format(use_dir,f)
            creation_time = os.path.getctime(full_f)
            if (current_time - creation_time) // (24 * 3600) >= 7:
                os.unlink(full_f)
                msg = 'File deleted: {}'.format(full_f)
                msg_all += '\r\n'
                msg_all += msg
                _logger.info(msg)
        #endregion DELETE LOG > 7 DAYS

        return msg_all

    @api.multi
    def action_backup_db(self):
        msg = self.backup_db()
        return Util.jek_pop1(msg)

    def backup_db(self):
        msg_all = ''
        # import odoo.addons.web.controllers.main as main
        from odoo.tools import config
        admin_passwd = config.get('admin_passwd', 'admin')
        db_name = config.get('db_name')
        if not db_name:
            db_name = self.env.cr.dbname
        backup_format = 'zip'

        import os
        import datetime
        import odoo
        import shutil

        today = datetime.datetime.today().strftime('%Y%m%d')
        old_file = config.get('logfile')
        if old_file:
            list_file_name = old_file.split('/')
            if len(list_file_name) > 1:
                old_file_name = list_file_name[len(list_file_name)-1]
                old_dir = old_file[:(len(old_file)-len(old_file_name)-1)] #1 = back slash terakhir
            else:
                old_file_name = old_file
                old_dir = '.'
        else:
            old_file_name = 'odoo-server.log'

            import getpass
            username = getpass.getuser() or 'odoo'
            old_dir = '/var/log/{}'.format(username)

            old_file = "{}/{}".format(old_dir, old_file_name)

        bak_dir = "{}/db_backup".format(old_dir)
        if not os.path.exists(bak_dir):
            os.makedirs(bak_dir)

        use_dir = bak_dir

        new_file_name = "{}-{}.zip".format(db_name,today)
        new_file = os.path.join(use_dir, new_file_name)
        exists_new = os.path.isfile(new_file)
        x=1
        while exists_new:
            x+=1
            new_file_name = "{}-{}-{}.zip".format(db_name, today, x)
            new_file = os.path.join(use_dir, new_file_name)
            exists_new = os.path.isfile(new_file)

        import tempfile
        # stream = tempfile.TemporaryFile()
        stream = tempfile.NamedTemporaryFile(delete=False)
        odoo.service.db.dump_db(db_name=db_name, stream=stream, backup_format=backup_format)
        stream.seek(0)
        stream.close()
        shutil.copy(stream.name, new_file)
        os.unlink(stream.name)

        msg = "###Backup DB! {}".format(new_file)
        msg_all += '\r\n'
        msg_all += msg
        _logger.info(msg)

        #region DELETE  > 7 DAYS
        import time
        current_time = time.time()
        for f in os.listdir(path=use_dir):
            full_f = '{}/{}'.format(use_dir,f)
            creation_time = os.path.getctime(full_f)
            if (current_time - creation_time) // (24 * 3600) >= 7:
                os.unlink(full_f)
                msg = 'File deleted: {}'.format(full_f)
                msg_all += '\r\n'
                msg_all += msg
                _logger.info(msg)
        #endregion DELETE  > 7 DAYS

        return msg_all

    def get_setup(self):
        rec = self.search([], order='id desc', limit=1)
        if not rec:
            rec = self.create({})
        return rec

class MailMail(models.Model):
    _inherit = 'mail.mail'

    # @api.model
    # def create(self, values):
    #         _logger.info('##################Return False (1) on Create Email')
    #         raise ValidationError(_('NO!!!!!'))
    #
    # @api.model
    # def create(self, values):
    #     row_custom = self.search([], limit=1, order="id desc")
    #     web_base_url = row_custom.web_base_url
    #     app_title = row_custom.name
    #
    #     wrong_odoo_url = web_base_url + '/www.odoo.com'
    #
    #     subject = values.get('subject')
    #     subject = str(subject).replace(wrong_odoo_url, web_base_url)
    #     subject = str(subject).replace('www.odoo.com', web_base_url)
    #     subject = str(subject).replace('Odoo', app_title)
    #     subject = str(subject).replace('odoo', app_title)
    #
    #     body = values.get('body')
    #     body = str(body).replace(wrong_odoo_url, web_base_url)
    #     body = str(body).replace('www.odoo.com', web_base_url)
    #     body = str(body).replace('Odoo', app_title)
    #     body = str(body).replace('odoo', app_title)
    #
    #     body_html = values.get('body_html')
    #     body_html = str(body_html).replace(wrong_odoo_url, web_base_url)
    #     body_html = str(body_html).replace('www.odoo.com', web_base_url)
    #     body_html = str(body_html).replace('Odoo', app_title)
    #     body_html = str(body_html).replace('odoo', app_title)
    #
    #     values['subject'] = subject
    #     values['body'] = body
    #     values['body_html'] = body_html
    #
    #     rec = super(MailMail, self).create(values)
    #     return rec

    @api.multi
    def send(self, auto_commit=False, raise_exception=False):
        for rec in self:
            subject = rec.subject

            if subject == 'Password reset':
                super(MailMail, self).send()
            else:
                row_custom = Util.get_setup(self)
                white_list_email = row_custom.white_list_email
                list_white_list_email = [one.login for one in white_list_email]

                email_list = []
                if rec.email_to:
                    email_list.append(rec.email_to)
                for partner in rec.recipient_ids:
                    email_list.append(partner.email)

                for email in email_list:
                    if email in list_white_list_email:
                        _logger.info('##################Send Email : %s ', email)
                        super(MailMail, self).send()
                    else:
                        _logger.info('##################Blocked Email : %s ', email)
                        # Memastikan tidak ada yang outstanding
                        self.cancel()
                        return False
