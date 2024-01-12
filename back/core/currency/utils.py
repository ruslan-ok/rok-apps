from datetime import date, timedelta
from decimal import Decimal
from core.models import CurrencyRate
from core.currency.custom_api.api_factory import ExchangeRateApiFactory
from logs.logger import get_logger

logger = get_logger(__name__, 'currency', 'exchange_rate')

def get_exchange_rate_for_api(date: date, currency: str, base: str='USD', rate_api: str|None=None, skip_db: str|None=None) -> tuple[CurrencyRate|None, str|None]:
    currency_rate = None
    info = ''
    try:
        if skip_db != 'yes':
            rate_db = _get_db_exchange_rate(date, currency)
            if rate_db:
                return rate_db, 'The value stored in the database was used'
        api_factory = ExchangeRateApiFactory()
        api = api_factory.get_api(rate_api)
        currency_rate, info = api.get_rate_on_date(date, currency, base)
    except Exception as ex:
        logger.exception(ex)
        info = 'Exception in get_exchange_rate_for_api()'
    return currency_rate, info

def _get_db_exchange_rate(date: date, currency: str) -> CurrencyRate|None:
    if CurrencyRate.objects.filter(base='USD', currency=currency, date__lte=date).exists():
        last_dt = CurrencyRate.objects.filter(base='USD', currency=currency, date__lte=date).order_by('-date')[0].date
        rate = CurrencyRate.objects.filter(base='USD', currency=currency, date=last_dt).order_by('source')[0]
        return rate
    return None

def get_hist_exchange_rates(beg: date, end: date, currency: str) -> list[Decimal]:
    ret = []
    rates = CurrencyRate.objects.filter(base='USD', currency=currency, date__range=(beg, end))
    all_rates = []
    for rate in rates:
        all_rates.append((rate.date, rate.value, _sort_exchange_rate_by_source(rate.source)))
    prev_day_rate = None
    date = beg
    while date <= end:
        rate = None
        day_rates = [x for x in all_rates if x[0] == date]
        day_rates = sorted(day_rates, key=lambda x: x[2])
        if len(day_rates):
            rate = day_rates[0][1]
            prev_day_rate = rate
        else:
            if prev_day_rate:
                rate = prev_day_rate
            else:
                rates = CurrencyRate.objects.filter(base='USD', currency=currency, date__lt=beg).order_by('-date')
                if len(rates):
                    rate = rates[0].value / rates[0].num_units
                    prev_day_rate = rate
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
