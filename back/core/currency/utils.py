from datetime import date, datetime, timedelta
from core.models import CurrencyRate, CurrencyApis
from core.currency.exchange_rate_api import *


def get_exchange_rate_for_api(date: date, currency: str, base: str='USD', rate_api: str|None=None, skip_db: str|None=None) -> tuple[Decimal|None, str|None]:
    if skip_db != 'yes':
        rate_db = _get_db_exchange_rate(date, currency)
        if rate_db:
            return rate_db, None
    match rate_api:
        case 'ecb':   api = CurrencyApis.objects.filter(name='ecb.europa.eu').get()
        case 'nbp':   api = CurrencyApis.objects.filter(name='api.nbp.pl').get()
        case 'nbrb':  api = CurrencyApis.objects.filter(name='belta.by').get()
        case 'boe':   api = CurrencyApis.objects.filter(name='bankofengland.co.uk').get()
        case 'er':    api = CurrencyApis.objects.filter(name='api.exchangerate.host').get()
        case 'ca':    api = CurrencyApis.objects.filter(name='currencyapi.com').get()
        case _:       api = None
    if api:
        api_obj = ExchangeRateApi(api)
        rate, info = api_obj.get_rate_on_date(date, currency, base)
    else:
        rate, info = _get_net_exchange_rate(date, currency, base)
    return rate, info

def _get_db_exchange_rate(date: date, currency: str) -> Decimal|None:
    if CurrencyRate.objects.filter(base='USD', currency=currency, date__lte=date).exists():
        last_dt = CurrencyRate.objects.filter(base='USD', currency=currency, date__lte=date).order_by('-date')[0].date
        rate = CurrencyRate.objects.filter(base='USD', currency=currency, date=last_dt).order_by('source')[0]
        return rate.value
    return None

def _get_net_exchange_rate(date: date, currency: str, base: str='USD') -> tuple[Decimal|None, str|None]:
    rate = None
    info = f'Not found external currency exchange rate API for pair {currency}/{base} [{date=}]'
    for api in CurrencyApis.objects.exclude(next_try__gt=datetime.today().date()):
        if date == datetime.today().date() and not api.today_avail:
            continue
        api_obj = ExchangeRateApi(api)
        rate, info = api_obj.get_rate_on_date(date, currency, base)
        if rate:
            break
    return rate, info

def get_hist_exchange_rates(beg: date, end: date, currency: str) -> list[Decimal]:
    ret = []
    rates = CurrencyRate.objects.filter(base='USD', currency=currency, date__range=(beg, end))
    all_rates = []
    for rate in rates:
        all_rates.append((rate.date, rate.value, _sort_exchange_rate_by_source(rate.source)))
    date = beg
    while date <= end:
        rate = None
        day_rates = [x for x in all_rates if x[0] == date]
        day_rates = sorted(day_rates, key=lambda x: x[2])
        if len(day_rates):
            rate = day_rates[0][1]
        else:
            rate, info = get_exchange_rate_for_api(date, currency)
        ret.append(rate if rate else Decimal(1))
        date = date + timedelta(1)
    return ret

def _sort_exchange_rate_by_source(source):
    match source:
        case 'nbrb.by': return 1
        case 'etalonline.by': return 2
        case 'currencyapi.com': return 3
        case 'api.exchangerate.host': return 4
        case 'GoogleFinanse': return 5
        case _: return 6
