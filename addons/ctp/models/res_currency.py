from odoo import api, fields, models


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    buy_rate = fields.Float(compute='_compute_current_buy_rate', string='Buy Rate', digits=(12, 6),
                        help='The buy rate of the currency to the currency of rate 1.')

    sale_rate = fields.Float(compute='_compute_current_sale_rate', string='Sale Rate', digits=(12, 6),
                            help='The sale rate of the currency to the currency of rate 1.')

    def _get_buy_rates(self, company, date):
        query = """SELECT c.id,
                          COALESCE((SELECT r.buy_rate FROM res_currency_rate r
                                  WHERE r.currency_id = c.id AND r.name <= %s
                                    AND (r.company_id IS NULL OR r.company_id = %s)
                               ORDER BY r.company_id, r.name DESC
                                  LIMIT 1), 1.0) AS buy_rate                
                   FROM res_currency c
                   WHERE c.id IN %s"""
        self._cr.execute(query, (date, company.id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        return currency_rates

    def _get_sale_rates(self, company, date):
        query = """SELECT c.id,
                          COALESCE((SELECT r.sale_rate FROM res_currency_rate r
                                  WHERE r.currency_id = c.id AND r.name <= %s
                                    AND (r.company_id IS NULL OR r.company_id = %s)
                               ORDER BY r.company_id, r.name DESC
                                  LIMIT 1), 1.0) AS sale_rate                
                   FROM res_currency c
                   WHERE c.id IN %s"""
        self._cr.execute(query, (date, company.id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        return currency_rates

    @api.model
    def _get_conversion_rate(self, from_currency, to_currency, company, date):
        rate = super()._get_conversion_rate(
            from_currency,
            to_currency,
            company,
            date
        )
        return 1 / rate

    @api.multi
    @api.depends('rate_ids.rate')
    def _compute_current_buy_rate(self):
        date = self._context.get('date') or fields.Date.today()
        company = self.env['res.company'].browse(self._context.get('company_id')) or self.env['res.users']._get_company()
        # the subquery selects the last rate before 'date' for the given currency/company
        currency_buy_rates = self._get_buy_rates(company, date)
        for currency in self:
            currency.buy_rate = currency_buy_rates.get(currency.id) or 1.0

    @api.multi
    @api.depends('rate_ids.rate')
    def _compute_current_sale_rate(self):
        date = self._context.get('date') or fields.Date.today()
        company = self.env['res.company'].browse(self._context.get('company_id')) or self.env['res.users']._get_company()
        # the subquery selects the last rate before 'date' for the given currency/company
        currency_sale_rates = self._get_sale_rates(company, date)
        for currency in self:
            currency.sale_rate = currency_sale_rates.get(currency.id) or 1.0

class ResCurrencyRate(models.Model):
    _name = 'res.currency.rate'
    _inherit = ['res.currency.rate', 'mail.thread']

    buy_rate = fields.Float(string='Buy Rate', digits=(12, 6),
                            help='The buy rate of the currency to the currency of rate 1.')

    sale_rate = fields.Float(string='Sale Rate', digits=(12, 6),
                             help='The sale rate of the currency to the currency of rate 1.')
