# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.jekdoo.utils.util import Util

from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class ReportPPH(models.TransientModel):
    _name = 'berdikari.report.pph'
    _description = 'Report PPH'

    date_start = fields.Date()
    date_end = fields.Date()

    bahan_baku_awal = fields.Float(string="Awal")
    bahan_baku_pembelian = fields.Float(string="Pembelian")
    bahan_baku_akhir = fields.Float(string="Akhir")

    total_biaya = fields.Float()

    biaya_awal = fields.Float(string="Awal")
    biaya_pindah = fields.Float(string="Pindah Bahan + Biaya")
    biaya_akhir = fields.Float(string="Akhir")
    total_hpp_proses = fields.Float(string="Total HPP Proses")

    jadi_awal = fields.Float(string="Awal")
    jadi_pindah = fields.Float(string="Pindah WIP")
    jadi_akhir = fields.Float(string="Akhir")
    total_hpp_produksi = fields.Float(string="Total HPP Produksi")

    def go_action(self):
        for rec in self:
            if not rec.date_start:
                raise ValidationError(_('Date Start tidak boleh kosong'))

            if not rec.date_end:
                raise ValidationError(_('Date End tidak boleh kosong'))

            setup = rec.env['jekdoo.setup'].get_setup()
            if not setup.asset_account_id:
                raise ValidationError(_('Asset Account belum dipilih di Custom Configuration'))

            if not setup.prefix_akun_biaya:
                raise ValidationError(_('Prefix Akun Biaya belum dipilih di Custom Configuration'))

            if not setup.wip_account_id:
                raise ValidationError(_('WIP Account belum dipilih di Custom Configuration'))

            account_code = setup.asset_account_id.code
            date_start = rec.date_start.strftime('%Y-%m-%d')
            date_end = rec.date_end.strftime('%Y-%m-%d')

            ########################################################################################################################
            logos = '''
                    select (sum(a.debit) - sum(a.credit)) as asset_awal  
                    from account_move_line a 
                    join account_account b on b.id = a.account_id 
                    where b.code = %s
                    and a.date < %s
                    group by b.code
            '''
            self._cr.execute(logos, (account_code, date_start))
            rows = self._cr.fetchall()
            bahan_baku_awal = 0
            if rows:
                row = rows[0]
                bahan_baku_awal = row[0]
            rec.bahan_baku_awal = bahan_baku_awal


            logos = '''
                select sum(a.debit) as sum_debit    
                from account_move_line a 
                join account_account b on b.id = a.account_id 
                where b.code = %s
                and a.date >= %s
                and a.date < %s
                group by b.code
            '''
            self._cr.execute(logos, (account_code, date_start, date_end))
            rows = self._cr.fetchall()
            bahan_baku_pembelian = 0
            bahan_baku_akhir = 0
            if rows:
                row = rows[0]
                bahan_baku_pembelian = row[0]
                bahan_baku_akhir = bahan_baku_awal + bahan_baku_pembelian
            rec.bahan_baku_pembelian = bahan_baku_pembelian
            rec.bahan_baku_akhir = bahan_baku_akhir


            logos = '''
                select sum(a.debit) as sum_debit    
                from account_move_line a 
                join account_account b on b.id = a.account_id 
                where b.code = %s
                and a.date >= %s
                and a.date < %s
                group by b.code
            '''
            self._cr.execute(logos, (account_code, date_start, date_end))
            rows = self._cr.fetchall()
            bahan_baku_pembelian = 0
            bahan_baku_akhir = 0
            if rows:
                row = rows[0]
                bahan_baku_pembelian = row[0]
                bahan_baku_akhir = bahan_baku_awal + bahan_baku_pembelian
            rec.bahan_baku_pembelian = bahan_baku_pembelian
            rec.bahan_baku_akhir = bahan_baku_akhir

            ########################################################################################################################

            prefix_biaya = '{}%'.format(setup.prefix_akun_biaya)
            logos = '''
                select sum(a.debit) as sum_debit    
                from account_move_line a 
                join account_account b on b.id = a.account_id 
                where b.code like %s
                and a.date >= %s
                and a.date < %s
                group by b.code
            '''
            self._cr.execute(logos, (prefix_biaya, date_start, date_end))
            rows = self._cr.fetchall()
            total_biaya = 20242
            if rows:
                row = rows[0]
                total_biaya = row[0]
            rec.total_biaya = total_biaya

            wip_account_code = setup.wip_account_id.code
            logos = '''
                    select (sum(a.debit) - sum(a.credit)) as asset_awal  
                    from account_move_line a 
                    join account_account b on b.id = a.account_id 
                    where b.code = %s
                    and a.date < %s
                    group by b.code
            '''
            self._cr.execute(logos, (wip_account_code, date_start))
            rows = self._cr.fetchall()
            biaya_awal = 0
            if rows:
                row = rows[0]
                biaya_awal = row[0]
            biaya_pindah = total_biaya
            biaya_akhir = 0
            total_hpp_proses = biaya_awal + total_biaya

            rec.biaya_awal = biaya_awal
            rec.biaya_pindah = biaya_pindah
            rec.total_hpp_proses = total_hpp_proses
            ########################################################################################################################
            produk_jadi_account_code = setup.produk_jadi_account_id.code
            logos = '''
                    select (sum(a.debit) - sum(a.credit)) as asset_awal  
                    from account_move_line a 
                    join account_account b on b.id = a.account_id 
                    where b.code = %s
                    and a.date < %s
                    group by b.code
            '''
            self._cr.execute(logos, (produk_jadi_account_code, date_start))
            rows = self._cr.fetchall()
            jadi_awal = 0
            if rows:
                row = rows[0]
                jadi_awal = row[0]
            jadi_pindah = total_hpp_proses
            jadi_akhir = 0

            logos = '''
                    select (sum(a.debit) - sum(a.credit)) as asset_awal  
                    from account_move_line a 
                    join account_account b on b.id = a.account_id 
                    where b.code = %s
                    and a.date <= %s
                    group by b.code
                        '''
            self._cr.execute(logos, (produk_jadi_account_code, date_end))
            rows = self._cr.fetchall()
            jadi_akhir = 0
            if rows:
                row = rows[0]
                jadi_akhir = row[0]

            rec.jadi_awal = jadi_awal
            rec.jadi_pindah = jadi_pindah
            rec.jadi_akhir = jadi_akhir
            ########################################################################################################################

