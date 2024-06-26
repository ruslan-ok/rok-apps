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

    def get_rate_on_date(self, date: date, currency: str, base: str) -> tuple[CurrencyRate|None, str|None]:
        if not self.api:
            return None, 'Exchange rate API is undefined.'

        if self.api.base and currency != self.api.base and base != self.api.base:
            return None, f'Exchange rate API {self.api.name} supports only rates for {self.api.base} currency.'
        
        if self.api.next_try and self.api.next_try > datetime.today().date():
            return None, f'Exchange rate API {self.api.name} is blocked until date {self.api.next_try}.'

        if not self.api.weekdays_avail and date.weekday() in (5, 6):
            return None, f'The service {self.api.name} is not available on the weekday date {date.strftime('%Y-%m-%d')}.'
        
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
            try:
                info = json.loads(resp.text)['errors']['date'][0]
            except:
                info = f'Received response with code {resp.status_code}'
            return None, info
        try:
            currency_rate = self._process_resp(date, resp)
            return currency_rate, 'The value was obtained through the exchange rate API'

        except Exception as ex:
            logger.exception(ex)
            return None, str(ex)

    def store_rate(self, date: date, currency: str, base: str, num_units: int, value: Decimal, reverse: bool=False) -> CurrencyRate:
        rounded_value = round(value, 6)
        inverse_rate = None
        if CurrencyRate.objects.filter(base=base, currency=currency, rate_date=date, num_units=num_units, value=rounded_value, source=self.api.name).exists():
            currency_rate = CurrencyRate.objects.filter(base=base, currency=currency, rate_date=date, num_units=num_units, value=rounded_value, source=self.api.name)[0]
        else:
            currency_rate = CurrencyRate.objects.create(base=base, currency=currency, rate_date=date, num_units=num_units, value=rounded_value, source=self.api.name)
            if not reverse:
                effective_rate = value * num_units
                reverse_value = 1 / effective_rate
                inverse_rate = self.store_rate(date, base, currency, 1, reverse_value, True)
        if self.inverse and inverse_rate:
            return inverse_rate
        return currency_rate

    def sleep(self, days: int=30):
        if not self.api.next_try or self.api.next_try < datetime.today().date():
            self.api.next_try = datetime.today().date() + timedelta(days)
            self.api.save()
            logger.warning(f'API service {self.api.name} sleeps until {self.api.next_try.strftime('%Y-%m-%d')}')

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
        currency_rate = self.store_rate(date, self.currency, self.base, 1, value, self.inverse)
        return currency_rate

    def get_last_available_date(self) -> tuple[date|None, str]:
        date = None
        info = 'Exchange rate API is undefined.'
        if self.api:
            date = datetime.today().date()
            info = ''

            if self.api.next_try and self.api.next_try > date:
                return None, f'Exchange rate API {self.api.name} is blocked until date {self.api.next_try}.'

            if not self.api.today_avail:
                date -= timedelta(1)

            if not self.api.weekdays_avail and date.weekday() in (5, 6):
                return None, f'The service {self.api.name} is not available on the weekday date {date.strftime('%Y-%m-%d')}.'

        return date, info