import requests
from bs4 import BeautifulSoup
from odoo import fields, models
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = 'res.company'

    currency_provider = fields.Selection([
        ('bi', 'Bank Indonesia')
    ], default='bi', string='Service Provider')

    is_force_date_stock = fields.Boolean(default=False)
    is_force_date_sales_order = fields.Boolean(default=False)

    def _parse_bi_data(self, available_currencies):
        request_url = 'https://www.bi.go.id/id/moneter/informasi-kurs/transaksi-bi/Default.aspx'
        try:
            web_page = requests.request('GET', request_url).text
        except:
            return False

        soup = BeautifulSoup(web_page)
        rates_dict = {}
        tables = soup.find_all('table', id='ctl00_PlaceHolderMain_biWebKursTransaksiBI_GridView1')
        for table in tables:
            trs = table.find_all('tr')
            available_currency_names = available_currencies.mapped('name')
            for tr in trs:
                datas = [tag.text.strip() for tag in tr.find_all('td')]
                if len(datas) == 5 and datas[0] in available_currency_names:
                    currency_code = datas[0]
                    #rates_dict[currency_code] = (float(datas[1]) / float(datas[3].replace(',', '')), fields.Date.today())
                    buy_rate = float(datas[2].replace(',', '')) / float(datas[1])
                    sale_rate = float(datas[3].replace(',', '')) / float(datas[1])
                    rate = (buy_rate + sale_rate) / 2
                    rates_dict[currency_code] = (rate, buy_rate, sale_rate, fields.Date.today())

        if 'IDR' in available_currency_names:
            rates_dict['IDR'] = (1.0, 1.0, 1.0, fields.Date.today())

        return rates_dict

    def _generate_currency_rates(self, parsed_data):
        """ Generate the currency rate entries for each of the companies, using the
        result of a parsing function, given as parameter, to get the rates data.

        This function ensures the currency rates of each company are computed,
        based on parsed_data, so that the currency of this company receives rate=1.
        This is done so because a lot of users find it convenient to have the
        exchange rate of their main currency equal to one in Odoo.
        """
        Currency = self.env['res.currency']
        CurrencyRate = self.env['res.currency.rate']

        today = fields.Date.today()
        for company in self:
            rate_info = parsed_data.get(company.currency_id.name, None)

            if not rate_info:
                raise UserError(_("Your main currency (%s) is not supported by this exchange rate provider. Please choose another one.") % company.currency_id.name)

            base_currency_rate = rate_info[0]
            #buy_rate, sale_rate
            for currency, (rate, buy_rate, sale_rate, date_rate) in parsed_data.items():
                rate_value = rate/base_currency_rate
                buy_rate_value = buy_rate/base_currency_rate
                sale_rate_value = sale_rate/base_currency_rate

                currency_object = Currency.search([('name','=',currency)])
                already_existing_rate = CurrencyRate.search([('currency_id', '=', currency_object.id), ('name', '=', date_rate), ('company_id', '=', company.id)])
                if already_existing_rate:
                    already_existing_rate.rate = rate_value
                    already_existing_rate.buy_rate = buy_rate_value
                    already_existing_rate.sale_rate = sale_rate_value
                else:
                    CurrencyRate.create({'currency_id': currency_object.id, 'rate': rate_value, 'buy_rate': buy_rate_value, 'sale_rate': sale_rate_value, 'name': date_rate, 'company_id': company.id})
