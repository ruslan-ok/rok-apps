from decimal import Decimal
from lxml import etree
from core.currency.custom_api.exchange_rate_api import ExchangeRateApi
from core.models import CurrencyRate


class Myfin(ExchangeRateApi):
    
    def __init__(self):
        super().__init__('myfin.by')

    def _process_resp(self, date, resp) -> CurrencyRate:
        tree = etree.HTML(resp.text, parser=None)
        r = tree.xpath("//table[contains(@class, 'default-table')]/tbody/tr")
        rates = {}
        for x in r:
            if len(x) in (4,5):
                correct = len(x) - 4
                rate_currency = x[2 + correct][0].tail
                rate_value = Decimal(x[1].text)
                num_units = int(x[3 + correct].text)
                rates[rate_currency] = {
                    'value': rate_value,
                    'num_units': num_units,
                }
        value = rates[self.currency]['value']
        num_units = rates[self.currency]['num_units']
        if self.inverse:
            value = 1 / value
        rate = self.store_rate(date, self.currency, self.base, num_units, value)
        return rate
