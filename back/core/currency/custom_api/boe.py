from decimal import Decimal
from lxml import etree
from core.currency.custom_api.exchange_rate_api import ExchangeRateApi
from core.models import CurrencyRate

BOE_CURRENCIES = {
    'Australian Dollar': 'AUD',
    'Canadian Dollar': 'CAD',
    'Chinese Yuan': 'CNY',
    'Czech Koruna': 'CZK',
    'Danish Krone': 'DKK',
    'Euro': 'EUR',
    'Hong Kong Dollar': 'HKD',
    'Hungarian Forint': 'HUF',
    'Indian Rupee': 'INR',
    'Israeli Shekel': 'ILR',
    'Japanese Yen': 'JPY',
    'Malaysian ringgit': 'MYR',
    'New Zealand Dollar': 'NZD',
    'Norwegian Krone': 'NOK',
    'Polish Zloty': 'PLN',
    'Saudi Riyal': 'SAR',
    'Singapore Dollar': 'SGD',
    'South African Rand': 'ZAR',
    'South Korean Won': 'KRW',
    'Swedish Krona': 'SEK',
    'Swiss Franc': 'CHF',
    'Taiwan Dollar': 'TWD',
    'Thai Baht': 'THB',
    'Turkish Lira': 'TRY',
    'US Dollar': 'USD',
}


class BOE(ExchangeRateApi):
    
    def __init__(self):
        super().__init__('bankofengland.co.uk')

    def _process_resp(self, date, resp) -> CurrencyRate:
        tree = etree.HTML(resp.text, parser=None)
        e = tree.xpath("//*[@id='editorial']/p[contains(@class, 'error')]")
        if e:
            raise Exception(e[0].text)
        r = tree.xpath("//*[@id='editorial']/table/tr")
        rates = {}
        for x in r:
            if len(x) == 4:
                rate_currency = BOE_CURRENCIES[x[0].xpath("./*")[0].text]
                rate_value = Decimal(x[1].text.split()[0])
                rates[rate_currency] = {'value': rate_value}
        value = rates[self.currency]['value']
        if not self.inverse:
            value = 1 / value
        rate = self.store_rate(date, self.currency, self.base, 1, value)
        return rate
