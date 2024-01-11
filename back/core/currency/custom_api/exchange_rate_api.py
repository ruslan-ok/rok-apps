import requests, json
from datetime import date, datetime, timedelta
from decimal import Decimal
from rest_framework import status
from core.models import CurrencyRate, CurrencyApis
from logs.logger import get_logger


logger = get_logger(__name__, 'currency', 'exchange_rate')


class ExchangeRateApi:

    def __init__(self, api_name: str|None):
        super().__init__()
        self.api = None
        if api_name:
            self.api = CurrencyApis.objects.filter(name=api_name).get()
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    def _get_rate_on_date(self, date: date, currency: str, base: str='USD') -> tuple[CurrencyRate|None, str|None]:
        currency = currency.upper()
        base = base.upper()

        if not self.api:
            return None, 'Exchange rate API is undefined.'

        if self.api.base and currency != self.api.base and base != self.api.base:
            return None, f'Exchange rate API {self.api.name} supports only rates for {self.api.base} currency.'
        
        if self.api.next_try and self.api.next_try > datetime.today().date():
            return None, f'Exchange rate API {self.api.name} is blocked until date {self.api.next_try}.'

        if not self.api.weekdays_avail and date.weekday() in (5, 6):
            return None, f'The service {self.api.name} is not available on the weekday date {date.strftime('%Y-%m-%d')}.'
        
        if not self.api.today_avail and date == date.today():
            # The service is not available on the today date
            date = date - timedelta(1)
        
        if self.api.base and base != self.api.base:
            self.currency = base
            self.base = currency
            self.inverse = True
        else:
            self.currency = currency
            self.base = base
            self.inverse = False

        url = self.api.api_url.replace('{token}', self.api.token)
        url = url.replace('{base}', self.base)
        url = url.replace('{currency}', self.currency.upper())
        url = url.replace('{date}', date.strftime('%Y-%m-%d'))
        url = url.replace('{day}', str(date.day))
        url = url.replace('{month}', date.strftime('%b'))
        url = url.replace('{year}', str(date.year))
        headers = self.headers
        resp = requests.get(url, headers=headers)
        if (resp.status_code != status.HTTP_200_OK):
            if self.api.phrase and self.api.phrase in str(resp.content):
                self.sleep(30)
            error_mess = f'[x] Rate {currency} to base {base} on {date.strftime('%Y-%m-%d')}: {self.api.name} - {resp.status_code}'
            return None, error_mess
        try:
            currency_rate = self._process_resp(date, resp)
            return currency_rate, ''

        except Exception as ex:
            error_mess =str(ex)
            if 'Supplied date cannot be greater than latest available data' in error_mess:
                logger.info(error_mess)
            else:
                logger.exception(ex)
            return None, error_mess

    def get_rate_on_date(self, date: date, currency: str, base: str='USD') -> tuple[CurrencyRate|None, str|None]:
        rate = num_units = None
        currency_rate, info = self._get_rate_on_date(date, currency, base)
        if not currency_rate and 'Supplied date cannot be greater than latest available data' in info:
            available_date_str = info.split('(')[1].split(')')[0]
            available_date = datetime.strptime(available_date_str, '%d-%b-%Y')
            currency_rate, info = self._get_rate_on_date(available_date, currency, base)
        if currency_rate:
            rate = currency_rate.value
            num_units = currency_rate.num_units
        logger.info({
            'action': 'api_call',
            'date': date.strftime('%Y-%m-%d'),
            'currency': currency.upper(),
            'base': base.upper(),
            'rate': str(rate),
            'num_units': num_units,
        })
        return currency_rate, info
    
    def store_rate(self, date: date, currency: str, base: str, num_units: int, value: Decimal, reverse: bool=False) -> CurrencyRate:
        rounded_value = round(value, 6)
        if CurrencyRate.objects.filter(base=base, currency=currency, date=date, num_units=num_units, value=rounded_value, source=self.api.name).exists():
            currency_rate = CurrencyRate.objects.filter(base=base, currency=currency, date=date, num_units=num_units, value=rounded_value, source=self.api.name)[0]
        else:
            logger.info({
                'action': 'store_rate',
                'date': date.strftime('%Y-%m-%d'),
                'currency': currency,
                'base': base,
                'num_units': num_units,
                'rate': str(rounded_value),
            })
            currency_rate = CurrencyRate.objects.create(base=base, currency=currency, date=date, num_units=num_units, value=rounded_value, source=self.api.name)
            if not reverse:
                effective_rate = value * num_units
                reverse_value = 1 / effective_rate
                self.store_rate(date, base, currency, 1, reverse_value, True)
        return currency_rate

    def sleep(self, days: int=30):
        if not self.api.next_try or self.api.next_try < datetime.today().date():
            self.api.next_try = datetime.today().date() + timedelta(days)
            self.api.save()
            logger.warning(f'API service {self.api.name} sleep until {self.api.next_try.strftime('%Y-%m-%d')}')

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

    def _process_resp(self, date, resp) -> CurrencyRate:
        resp_json = json.loads(resp.content)
        value_path = self.api.value_path.replace('<currency>', self.currency).split('/')
        value = self.parse_value_path(resp_json, value_path)
        if not value:
            raise Exception('api.value_path parsing error')
        if self.api.base and self.inverse:
            value = 1 / value
        currency_rate = self.store_rate(date, self.currency, self.base, 1, value)
        return currency_rate
