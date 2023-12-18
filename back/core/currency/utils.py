from datetime import date, datetime, timedelta
from rest_framework import status
from core.models import CurrencyRate, CurrencyApis
from core.currency.exchange_rate_api import *

def get_db_exchange_rate(currency: str, date: date):
    if CurrencyRate.objects.filter(base='USD', currency=currency, date__lte=date).exists():
        last_dt = CurrencyRate.objects.filter(base='USD', currency=currency, date__lte=date).order_by('-date')[0].date
        rate = CurrencyRate.objects.filter(base='USD', currency=currency, date=last_dt).order_by('source')[0]
        return rate
    print('get_db_exchange_rate(currency=' + currency + ', date=' + date.strftime('%Y.%m.%d') + ')')
    return None

def get_net_exchange_rate(currency: str, date: date, base: str='USD') -> CA_Result:
    ret = CA_Result(result=CA_Status.unimpl)
    for api in CurrencyApis.objects.exclude(next_try__gt=datetime.today().date()):
        if date == datetime.today().date() and not api.today_avail:
            continue
        api_obj = ExchangeRateApi(api)
        ret = api_obj.get_rate_on_date(currency, date, base)
        print(f"get_net_exchange_rate({currency=}, date={date.strftime('%Y.%m.%d')}, {base=}), api={api.name}, result={ret.result}")
        if ret.result == CA_Status.ok:
            break
    return ret

def get_exchange_rate(currency: str, date: date) -> CA_Result:
    rate_db = get_db_exchange_rate(currency, date)
    if rate_db:
        if rate_db.date == date:
            return CA_Result(result=CA_Status.ok, status=status.HTTP_200_OK, rate=rate_db)
    return get_net_exchange_rate(currency, date)

def get_hist_exchange_rates(currency: str, beg: date, end: date) -> list:
    ret = []
    rates = CurrencyRate.objects.filter(base='USD', currency=currency, date__range=(beg, end))
    all_rates = []
    for rate in rates:
        all_rates.append((rate.date, rate.value, sort_exchange_rate_by_source(rate.source)))
    date = beg
    while date <= end:
        rate = None
        day_rates = [x for x in all_rates if x[0] == date]
        day_rates = sorted(day_rates, key=lambda x: x[2])
        if len(day_rates):
            rate = day_rates[0][1]
        else:
            rate_info = get_exchange_rate(currency, date)
            if rate_info and rate_info.result == CA_Status.ok and rate_info.rate:
                rate = rate_info.rate.value
        ret.append(rate)
        date = date + timedelta(1)
    return ret

def sort_exchange_rate_by_source(source):
    match source:
        case 'nbrb.by': return 1
        case 'etalonline.by': return 2
        case 'currencyapi.com': return 3
        case 'api.exchangerate.host': return 4
        case 'GoogleFinanse': return 5
        case _: return 6

def get_net_exchange_rate_for_api(rate_api: str, currency: str, date: date, base: str='USD') -> CA_Result:
    ret = CA_Result(result=CA_Status.unimpl)
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
        ret = api_obj.get_rate_on_date(currency, date, base)
    return ret
