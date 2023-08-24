import os, requests, json
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum
from rest_framework import status
from dataclasses import dataclass, field
# from logs.models import EventType, ServiceEvent
from task.const import APP_CORE, ROLE_CURRENCY
from logs.service_log import EventType, ServiceLog
from core.models import CurrencyRate, CurrencyApis

class CA_Status(Enum):
    ok = 'ok'
    error = 'error'
    unimpl = 'unimplemented'


@dataclass
class CA_Result:
    result: CA_Status = field(default=CA_Status.unimpl)
    status: int = field(default=status.HTTP_500_INTERNAL_SERVER_ERROR)
    rate: CurrencyRate|None = field(default=None)
    info: str = field(default='')

class ExchangeRateApi():

    def __init__(self, api: CurrencyApis):
        super().__init__()
        self.api = api
        self.headers = {'User-Agent': 'Mozilla/5.0'}
        this_device = os.environ.get('DJANGO_DEVICE', '')
        self.log = ServiceLog(this_device, APP_CORE, ROLE_CURRENCY)

    def get_rate_on_date(self, currency: str, date: date, base: str='USD') -> CA_Result:
        url = self.api.api_url.replace('{token}', self.api.token).replace('{currency}', currency).replace('{date}', date.strftime('%Y-%m-%d'))
        resp = requests.get(url, headers=self.headers)
        if (resp.status_code != status.HTTP_200_OK):
            if self.api.phrase and self.api.phrase in str(resp.content):
                self.sleep(30)
            info = json.loads(resp.content)
            self.log.write(type=EventType.ERROR, name='get_rate_on_date', info=f'[x] Rate {currency} to base {base} on {date.strftime("%Y-%m-%d")}: {self.api.name} - {resp.status_code} - {info}')
            return CA_Result(result=CA_Status.error, status=resp.status_code, info=info)
        try:
            resp_json = json.loads(resp.content)
            value_path = self.api.value_path.replace('<currency>', currency).split('/')
            value = self.parse_value_path(resp_json, value_path)
            if value:
                rate = self.store_rate(currency=currency, date=date, value=value)
                return CA_Result(CA_Status.ok, rate=rate, status=resp.status_code)
        except:
            info = json.loads(resp.content)
            self.log.write(type=EventType.ERROR, name='get_rate_on_date', info=f'[x] Rate {currency} to base {base} on {date.strftime("%Y-%m-%d")}: {self.api.name} - {info}')
            return CA_Result(result=CA_Status.error, status=status.HTTP_400_BAD_REQUEST, info=info)
        self.log.write(type=EventType.ERROR, name='get_rate_on_date', info=f'[x] Rate {currency} to base {base} on {date.strftime("%Y-%m-%d")}: unimplemented')
        return CA_Result(result=CA_Status.unimpl)
    
    def store_rate(self, currency: str, date: date, value, base: str='USD', num_units: int=1) -> CurrencyRate:
        self.log.write(type=EventType.INFO, name='store_rate', info=f'Rate {currency} to base {base} on {date.strftime("%Y-%m-%d")} is {value} by source {self.api.name}')
        return CurrencyRate.objects.create(base=base, currency=currency, date=date, num_units=num_units, value=value, source=self.api.name)

    def sleep(self, days: int=30):
        if not self.api.next_try or self.api.next_try < datetime.today().date():
            self.api.next_try = datetime.today().date() + timedelta(days)
            self.api.save()
            self.log.write(type=EventType.WARNING, name='sleep', info=f'API service {self.api.name} sleep until {self.api.next_try.strftime("%Y-%m-%d")}')

    def parse_value_path(self, resp_json: dict, value_path: list[str]) -> Decimal|None:
        match len(value_path):
            case 0: return None
            case 1: return round(Decimal(resp_json[value_path[0]]), 6)
            case _: return self.parse_value_path(resp_json[value_path[0]], value_path[1:])