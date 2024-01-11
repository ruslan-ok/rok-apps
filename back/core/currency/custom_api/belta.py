from datetime import datetime
from decimal import Decimal
from lxml import etree
from core.currency.custom_api.exchange_rate_api import ExchangeRateApi
from core.models import CurrencyRate

BELTA_MONTHS = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12,
}


class Belta(ExchangeRateApi):
    
    def __init__(self):
        super().__init__('belta.by')

    def _process_resp(self, date, resp) -> CurrencyRate:
        tree = etree.HTML(resp.text, parser=None)
        cur_date = tree.xpath("//*[contains(@class, 'cur_date')]")[0]
        cur_date_text = cur_date.text
        cur_date_words = cur_date_text.split()
        day = int(cur_date_words[2])
        month = BELTA_MONTHS[cur_date_words[3]]
        year = int(cur_date_words[4].replace(',', ''))
        belta_date = datetime(year, month, day).date()
        if date != belta_date:
            raise Exception(f'Last available date is {belta_date.strftime('%Y-%m-%d')}')
        r = tree.xpath("//*[contains(@class, 'cur_table')]")[0]
        rates = {}
        for x in r:
            if len(x) == 4:
                rate_currency = x[0].text
                rate_qty = int(x[2].text.split()[0])
                rate_value = Decimal(x[3].text.split()[0])
                rates[rate_currency] = {'qty': rate_qty, 'value': rate_value}
        value = rates[self.currency]['value']
        if not self.inverse:
            value = 1 / value
        rate = self.store_rate(date, self.currency, self.base, 1, value)
        return rate
    
