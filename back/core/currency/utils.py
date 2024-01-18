from datetime import date, datetime, timedelta
from decimal import Decimal
from core.models import CurrencyRate
from core.currency.custom_api.api_factory import ExchangeRateApiFactory
from logs.logger import get_logger

logger = get_logger(__name__, 'currency', 'exchange_rate')

def get_exchange_rate_for_api(date: date, currency: str, base: str='USD', rate_api: str|None=None, mode: str='can_update') -> tuple[CurrencyRate|Decimal|None, str|None]:
    # mode = ['can_update', 'db_only', 'api_only', 'db_only_fd', 'api_only_fd']
    currency = currency.upper()
    base = base.upper()
    if currency == base:
        return Decimal(1), f'Same currency in pair: {base=}, {currency=}'
    
    shifted_info = ''

    if mode == 'db_only_fd':  # fixed date
        rate, info = _get_db_exchange_rate(date, currency, base)
    
    if mode == 'api_only_fd':  # fixed date
        rate, info = _get_api_exchange_rate(date, currency, base, rate_api)

    if mode == 'api_only_lad':  # last available date
        rate, info = _get_api_exchange_rate(date, currency, base, rate_api, True)
    
    if mode == 'db_only':
        rate, info = _get_db_exchange_rate(date, currency, base)
        if not rate:
            shifted_date, shifted_info = shift_date(date, info)
            if shifted_date:
                rate, info = _get_db_exchange_rate(shifted_date, currency, base)

    if mode == 'api_only':
        rate, info = _get_api_exchange_rate(date, currency, base, rate_api)
        if not rate:
            shifted_date, shifted_info = shift_date(date, info)
            if shifted_date:
                rate, info = _get_api_exchange_rate(shifted_date, currency, base, rate_api)

    if mode == 'can_update':
        rate, info = _get_db_exchange_rate(date, currency, base)
        if not rate:
            db_shifted_date, db_shifted_info = shift_date(date, info)
            rate, info = _get_api_exchange_rate(date, currency, base, rate_api)
            if not rate:
                shifted_date, shifted_info = shift_date(date, info)
                if shifted_date:
                    rate, info = _get_db_exchange_rate(shifted_date, currency, base)
                    if not rate:
                        rate, info = _get_api_exchange_rate(shifted_date, currency, base, rate_api)
                if not rate and db_shifted_date:
                    rate, info = _get_db_exchange_rate(db_shifted_date, currency, base)
                    shifted_info = db_shifted_info

    if shifted_info:
        if info:
            info += '. '
        info += shifted_info
    if info:
        info = ': ' + info

    if rate:
        message = f'{round(rate.value, 6)} {currency.upper()} per {rate.num_units} {base.upper()} as of {date.strftime('%Y-%m-%d')}{info}.'
        logger.info(message)
    else:
        message = f'Failed to get {currency.upper()} to {base.upper()} exchange rate as of {date.strftime('%Y-%m-%d')}{info}.'
        logger.warning(message)

    return rate, info


def shift_date(date, info):
    shifted_date = None
    if 'Supplied date cannot be greater than latest available data' in info:
        available_date = info.split('(')[1].split(')')[0]
        shifted_date = datetime.strptime(available_date, '%d-%b-%Y').date()
    if 'The service is not available on the today date' in info:
        shifted_date = date - timedelta(1)
    if 'is not available on the weekday date' in info:
        delta = date.weekday() - 4
        shifted_date = date - timedelta(delta)
    if 'Nearest available date is' in info:
        available_date = info.split(': ')[1]
        shifted_date = datetime.strptime(available_date, '%d-%b-%Y').date()
    if 'The date must be a date before or equal to ' in info:
        available_date = info.split('equal to ')[1].split()[0]
        shifted_date = datetime.strptime(available_date, '%Y-%m-%d').date()
    if shifted_date:
        return shifted_date, f'Date shifted {date} -> {shifted_date}.'
    return None, ''


def _get_db_exchange_rate(date: date, currency: str, base: str) -> CurrencyRate|None:
    if CurrencyRate.objects.filter(date=date, currency=currency, base=base).exists():
        rate = CurrencyRate.objects.filter(date=date, currency=currency, base=base).order_by('source')[0]
        return rate, 'The value stored in the database was used'
    if CurrencyRate.objects.filter(date__lte=date, currency=currency, base=base).exists():
        check_date = CurrencyRate.objects.filter(date__lte=date, currency=currency, base=base).order_by('-date')[0].date
        return None, 'Nearest available date is: ' + check_date.strftime('%d-%b-%Y')
    return None, 'There is no saved rate for the specified date'

def _get_api_exchange_rate(date: date, currency: str, base: str, rate_api: str|None, last_available_date: bool=False) -> CurrencyRate|None:
    api_factory = ExchangeRateApiFactory()
    api = api_factory.get_api(rate_api)
    check_date = date
    if last_available_date:
        check_date, info = api.get_last_available_date()
        if not check_date:
            return None, info
    rate, info = api.get_rate_on_date(check_date, currency, base)
    return rate, info


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
