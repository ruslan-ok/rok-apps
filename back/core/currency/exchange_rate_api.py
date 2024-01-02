import requests, json, io
from datetime import date, datetime, timedelta
from decimal import Decimal
import pandas as pd
from lxml import etree
from rest_framework import status
from core.models import CurrencyRate, CurrencyApis
#from logs.logger import Logger


#logger = Logger(__name__, local_only=True)

class ExchangeRateApi():

    def __init__(self, api: CurrencyApis):
        super().__init__()
        self.api = api
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    def _get_rate_on_date(self, date: date, currency: str, base: str='USD') -> tuple[Decimal|None, str|None]:
        currency = currency.upper()
        base = base.upper()

        if self.api.base and currency != self.api.base and base != self.api.base:
            info = f'Exchange rate API {self.api.name} supports only rates for {self.api.base} currency.'
            return None, info

        inverse = False
        if self.api.base and base != self.api.base:
            tmp = currency
            currency = base
            base = tmp
            inverse = True

        day_info = None

        if not self.api.today_avail and date == date.today():
            date = date - timedelta(1)
            day_info = f'Date corrected to {date.strftime("%Y-%m-%d")} because of core_currencyapi.today_avail == False.'
        
        if not self.api.weekdays_avail and date.weekday() in (5, 6):
            date = date - timedelta(date.weekday() - 4)
            day_info = f'Date corrected to {date.strftime("%Y-%m-%d")} because of core_currencyapi.weekdays_avail == False.'
        
        url = self.api.api_url.replace('{token}', self.api.token)
        url = url.replace('{base}', base)
        url = url.replace('{currency}', currency.upper())
        url = url.replace('{date}', date.strftime('%Y-%m-%d'))
        url = url.replace('{day}', str(date.day))
        url = url.replace('{month}', date.strftime('%b'))
        url = url.replace('{year}', str(date.year))
        headers = self.headers
        if self.api.name == 'ecb.europa.eu':
            headers.update({'Accept': 'text/csv'})
        resp = requests.get(url, headers=headers)
        if (resp.status_code != status.HTTP_200_OK):
            if self.api.phrase and self.api.phrase in str(resp.content):
                self.sleep(30)
            if type(resp.content) == bytes:
                info = resp.content.decode('utf-8')
            else:
                info = json.loads(resp.content)
            error_mess = f'[x] Rate {currency} to base {base} on {date.strftime("%Y-%m-%d")}: {self.api.name} - {resp.status_code} - {info}'
            return None, error_mess
        try:
            if type(resp.content) == bytes and resp.text:
                if self.api.name == 'ecb.europa.eu':
                    return self.get_ecb_rate_on_date(currency, inverse, date, day_info, resp)
                if self.api.name == 'belta.by':
                    return self.get_belta_rate_on_date(currency, inverse, date, resp)
                if self.api.name == 'bankofengland.co.uk':
                    return self.get_boe_rate_on_date(currency, inverse, date, day_info, resp)

            resp_json = json.loads(resp.content)
            value_path = self.api.value_path.replace('<currency>', currency).split('/')
            value = self.parse_value_path(resp_json, value_path)
            if value:
                if self.api.base and not inverse:
                    value = 1 / value
                rate = self.store_rate(currency=currency, date=date, value=value)
                return rate.value, day_info
        except Exception as ex:
            if type(resp.content) == bytes:
                info = resp.content.decode('utf-8')
                if not info:
                    info = 'Exception in core > currency > exchange_rate_api.py > ExchangeRateApi > get_rate_on_date(): ' + str(ex)
            else:
                info = json.loads(resp.content)
            error_mess = f'[x] Rate {currency} to base {base} on {date.strftime("%Y-%m-%d")}: {self.api.name} - {info}'
            return None, error_mess

    def get_rate_on_date(self, date: date, currency: str, base: str='USD') -> tuple[Decimal|None, str|None]:
        rate, info = self._get_rate_on_date(date, currency, base)
        log_info = {
            'date': date.strftime('%Y-%m-%d'),
            'currency': currency,
            'base': base,
            'rate': rate.to_eng_string() if rate else None,
            'api': self.api.name,
            'info': info,
        }
        #logger.info(log_info)
        return rate, info
    
    def store_rate(self, currency: str, date: date, value, base: str='USD', num_units: int=1) -> CurrencyRate:
        return CurrencyRate.objects.create(base=base, currency=currency, date=date, num_units=num_units, value=round(value, 6), source=self.api.name)

    def sleep(self, days: int=30):
        if not self.api.next_try or self.api.next_try < datetime.today().date():
            self.api.next_try = datetime.today().date() + timedelta(days)
            self.api.save()
            #logger.warning(f'API service {self.api.name} sleep until {self.api.next_try.strftime("%Y-%m-%d")}')

    def parse_value_path(self, resp_json: dict, value_path: list[str]) -> Decimal|None:
        match len(value_path):
            case 0: return None
            case 1: return round(Decimal(resp_json[value_path[0]]), 6)
            case _:
                if value_path[0] == '0':
                    subdict = resp_json[0]
                else:
                    subdict = resp_json[value_path[0]]
                return self.parse_value_path(subdict, value_path[1:])

    def get_ecb_rate_on_date(self, currency, inverse, date, day_info, resp) -> tuple[Decimal|None, str|None]:
        df = pd.read_csv(io.StringIO(resp.text))
        s_value = df['OBS_VALUE']
        value = round(Decimal(s_value.values[0]), 6)
        if inverse:
            value = 1 / value
        rate = self.store_rate(currency=currency, date=date, value=value)
        return rate.value, day_info

    def get_belta_rate_on_date(self, currency, inverse, date, resp) -> tuple[Decimal|None, str|None]:
        tree = etree.HTML(resp.text, parser=None)
        cur_date = tree.xpath("//*[contains(@class, 'cur_date')]")[0]
        cur_date_text = cur_date.text
        cur_date_words = cur_date_text.split()
        day = int(cur_date_words[2])
        month = BELTA_MONTHS[cur_date_words[3]]
        year = int(cur_date_words[4].replace(',', ''))
        belta_date = datetime(year, month, day).date()
        day_info = ''
        if date != belta_date:
            day_info = f'Date corrected to {belta_date.strftime("%Y-%m-%d")} because of this is actual date on the site https://www.belta.by/currency/'
        r = tree.xpath("//*[contains(@class, 'cur_table')]")[0]
        rates = {}
        for x in r:
            if len(x) == 4:
                rate_currency = x[0].text
                rate_qty = int(x[2].text.split()[0])
                rate_value = Decimal(x[3].text.split()[0])
                rates[rate_currency] = {'qty': rate_qty, 'value': rate_value}
        value = rates[currency]['value']
        if not inverse:
            value = 1 / value
        rate = self.store_rate(currency=currency, date=belta_date, value=value)
        return rate.value, day_info
    
    def get_boe_rate_on_date(self, currency, inverse, date, day_info, resp) -> tuple[Decimal|None, str|None]:
        tree = etree.HTML(resp.text, parser=None)
        e = tree.xpath("//*[@id='editorial']/p[contains(@class, 'error')]")
        if e:
            return None, e[0].text
        r = tree.xpath("//*[@id='editorial']/table/tr")
        rates = {}
        for x in r:
            if len(x) == 4:
                rate_currency = BOE_CURRENCIES[x[0].xpath("./*")[0].text]
                rate_value = Decimal(x[1].text.split()[0])
                rates[rate_currency] = {'value': rate_value}
        value = rates[currency]['value']
        if inverse:
            value = 1 / value
        rate = self.store_rate(currency=currency, date=date, value=value)
        return rate.value, day_info
    
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
