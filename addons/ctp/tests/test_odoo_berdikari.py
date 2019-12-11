from datetime import datetime

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.addons.account.tests.account_test_classes import AccountingTestCase


class TestPurchaseOrder(AccountingTestCase):

    def setUp(self):
        super(TestPurchaseOrder, self).setUp()
        #Model-model yang akan dipakai
        self.PurchaseOrder = self.env['purchase.order']
        self.PurchaseOrderLine = self.env['purchase.order.line']
        self.Landing = self.env['stock.landed.cost']
        self.journal_misc = self.env['account.journal'].search([('code', '=', 'MISC')], limit=1)

        #Partner diset ke COBB
        self.partner_id = self.env.ref('__import__.id_berdikari_vendor_0490')
        #Product 1 : DOC GPS Female - D Line
        self.product_id_1 = self.env.ref('__export__.product_template_934_131e5d43')
        #Product 2 : DOC GPS Male - C Line
        self.product_id_2 = self.env.ref('__export__.product_template_935_f961bb01')
        #Product Expenses
        self.product_id_expense = self.env.ref('__export__.product_template_942_cb72d4a9')
        self.Flock = self.env['berdikari.flock.master']
        self.flock = self.create_flock()

    def _get_stock_input_move_lines(self, product_id):

        aml = self.env['account.move.line'].search([
            ('account_id', '=', self.product_id_1.categ_id.property_stock_account_input_categ_id.id),
            ('product_id', '=', product_id),
        ], order='id')
        return aml[-1]

    # def _get_stock_output_move_lines(self):
    #     return self.env['account.move.line'].search([
    #         ('account_id', '=', self.stock_output_account.id),
    #     ], order='date, id')
    #

    def _get_stock_valuation_move_lines(self, product_id):
        vml = self.env['account.move.line'].search([
            ('account_id', '=', self.product_id_1.categ_id.property_stock_valuation_account_id.id),
            ('product_id', '=', product_id)
        ], order='id')
        return vml[-1]

    def create_flock(self):
        return self.Flock.create({
            'code': 'PAS01-FLOCK01-201803',
            'name': 'PAS01-FLOCK01-201803',
            'company_id': self.env.user.company_id.id,
            'period_year': 2018,
            'period_sequence': 1
        })

    def test_01_create_flock_flow(self):
        #self.flock = self.create_flock()
        self.assertTrue(self.flock, 'Flock: no flock created')
        print("Format kode flock yang diharapkan sebagai contoh : PAS01-FLOCK02-201902")
        print("Flock ID : {0}".format(self.flock.id))

    def test_02_purchase_doc_flow(self):
        #self.flock = self.create_flock()
        print("Flock ID : {0}".format(self.flock.id))
        self.po_doc_vals = {
            'partner_id': self.partner_id.id,
            'date_order': '2018-03-01',
            'currency_id': self.env.ref("base.USD").id,
            'po_for': 'flock',
            'flock_id': self.flock.id,
            'order_line': [
                (0, 0, {
                    'name': self.product_id_1.name,
                    'product_id': self.product_id_1.id,
                    'product_qty': 12000.0,
                    'product_uom': self.product_id_1.uom_po_id.id,
                    'price_unit': 30.0,
                    'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                }),
                (0, 0, {
                    'name': self.product_id_2.name,
                    'product_id': self.product_id_2.id,
                    'product_qty': 8000.0,
                    'product_uom': self.product_id_2.uom_po_id.id,
                    'price_unit': 0.0,
                    'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                })
            ]
        }

        print("Create PO")
        self.po_doc_cobb = self.PurchaseOrder.create(self.po_doc_vals)
        print("Flock Code : {0}".format(self.po_doc_cobb.flock_id.code))
        self.assertTrue(self.po_doc_cobb, 'Purchase: no purchase order created')

        #Cek Kurs USD
        print("Kurs Saat Ini")
        self.po_doc_cobb_currency_rate = self.po_doc_cobb.currency_id.with_context(date=self.po_doc_cobb.date_order).rate or 1.0
        print(self.po_doc_cobb_currency_rate)

        print("Konfirmasi PO")
        self.po_doc_cobb.button_confirm()
        print("Purchase Order Nomor {0} berstatus : {1}".format(self.po_doc_cobb.name, self.po_doc_cobb.state))
        self.assertEqual(self.po_doc_cobb.state, 'purchase', 'Purchase: PO state should be "Purchase"')
        self.assertEqual(self.po_doc_cobb.picking_count, 1, 'Purchase: one picking should be created"')

        print("Receive Product")
        self.assertEqual(self.po_doc_cobb.picking_count, 1, 'Purchase: one picking should be created"')
        self.picking = self.po_doc_cobb.picking_ids[0]
        self.picking.write({'force_date': '2018-03-10'})
        self.picking.move_line_ids[0].write({'qty_done': 12000.0, 'lot_name': 'FMPAS001'})
        self.picking.move_line_ids[1].write({'qty_done': 8000.0, 'lot_name': 'FMPAS001'})

        print("Validate Receive Product")
        #todo:picking_date
        self.picking.button_validate()

        self.picking_currency_rate = self.po_doc_cobb.currency_id.with_context(date=self.picking.date_done).rate or 1.0
        print("Kurs pada saat picking")
        print(self.picking_currency_rate)

        self.assertEqual(self.po_doc_cobb.order_line.mapped('qty_received'), [12000.00, 8000.00],
                         'Purchase: all products should be received"')

        print('Costing method {}'.format(self.product_id_1.cost_method))
        print('Cek Inventory Valuation')
        print('-------------------------------------------------------------------------------------------------------')
        print('Valuation utk Product : {0} adalah {1} * {2} = {3}'.format(self.picking.move_lines[0].product_id.name,
                                                                          self.picking.move_lines[0].quantity_done,
                                                                          self.picking.move_lines[0].price_unit,
                                                                          self.picking.move_lines[0].price_unit *
                                                                          self.picking.move_lines[0].quantity_done
                                                                          ))

        self.assertEqual(self.picking.move_lines[0].value, 360000.0 * self.picking_currency_rate, "Nilai harus sama")

        print('Valuation utk Product : {0} adalah {1} * {2} = {3}'.format(self.picking.move_lines[1].product_id.name,
                                                                          self.picking.move_lines[1].quantity_done,
                                                                          self.picking.move_lines[1].price_unit,
                                                                          self.picking.move_lines[1].price_unit *
                                                                          self.picking.move_lines[1].quantity_done
                                                                          ))
        print('-------------------------------------------------------------------------------------------------------')
        self.assertEqual(self.picking.move_lines[1].value, 0.0, "Nilai harus 0")

        print('Landing Costs')
        self.landing = self.Landing.create({
            'l10n_mx_edi_customs_number': '15  48  3009  0001234',
            'picking_ids': [(4, self.picking.id)],
            'cost_lines': [(0, 0, {
                'product_id': self.product_id_expense.id,
                'price_unit': 20000000,
                'split_method': 'by_quantity',
            })],
            'account_journal_id': self.journal_misc.id,
        })
        self.landing.compute_landed_cost()
        self.landing.button_validate()

        self.landed_cost_1 = 20000000 * 12000 / 20000
        self.landed_cost_2 = 20000000 * 8000 / 20000

        print('Cek Inventory Valuation Setelah Landed Cost')
        print('-------------------------------------------------------------------------------------------------------')
        print('Valuation utk Product : {0} adalah {1} * {2} = {3}'.format(self.picking.move_lines[0].product_id.name,
                                                                          self.picking.move_lines[0].quantity_done,
                                                                          self.picking.move_lines[0].price_unit,
                                                                          self.picking.move_lines[0].price_unit *
                                                                          self.picking.move_lines[0].quantity_done
                                                                          ))

        self.assertEqual(self.picking.move_lines[0].value, 360000.0 * self.picking_currency_rate + self.landed_cost_1, "Nilai harus sama")

        print('Valuation utk Product : {0} adalah {1} * {2} = {3}'.format(self.picking.move_lines[1].product_id.name,
                                                                          self.picking.move_lines[1].quantity_done,
                                                                          self.picking.move_lines[1].price_unit,
                                                                          self.picking.move_lines[1].price_unit *
                                                                          self.picking.move_lines[1].quantity_done
                                                                          ))
        print('-------------------------------------------------------------------------------------------------------')
        self.assertEqual(self.picking.move_lines[1].value, 0.0 + self.landed_cost_2, "Nilai harus 0 + Landing Cost")

        # account values for move1
        input_aml = self._get_stock_input_move_lines(self.product_id_1.id)
        self.assertEqual(len(input_aml), 1)

        move1_input_aml = input_aml[-1]
        self.assertEqual(move1_input_aml.debit, 0)
        self.assertEqual(move1_input_aml.credit,
                         self.picking.move_lines[0].price_unit * self.picking.move_lines[0].quantity_done -
                         self.landed_cost_1)

        # account values for move2 (landed cost)
        input_aml_landed = self._get_stock_valuation_move_lines(self.product_id_1.id)
        self.assertEqual(len(input_aml_landed), 1)

        move1_input_aml_landed = input_aml_landed[-1]
        self.assertEqual(move1_input_aml_landed.credit, 0)
        self.assertEqual(move1_input_aml_landed.debit, self.landed_cost_1)


