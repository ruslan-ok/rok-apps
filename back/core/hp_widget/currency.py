import os, json, requests
from datetime import datetime, timedelta
from dataclasses import dataclass
from decimal import Decimal
from core.currency.utils import get_hist_exchange_rates
from core.hp_widget.delta import get_start_date, approximate, ChartPeriod, SourceData, build_chart_config

CURR_LIST = ('EUR', 'BYN', 'PLN', 'GBP', 'USD')

CURR_COLOR = {
    'USD': '72, 118, 47',
    'EUR': '61, 86, 170',
    'PLN': '179, 52, 52',
    'BYN': '132, 170, 61',
    'GBP': '136, 61, 170',
}

CURR_ICON = {
    'USD': 'bi-currency-dollar',
    'EUR': 'bi-currency-euro',
    'PLN': '',
    'BYN': '',
    'GBP': 'bi-currency-pound',
}

CURR_ABBR = {
    'USD': '',
    'EUR': '',
    'PLN': 'PLN',
    'BYN': 'BYN',
    'GBP': '',
}

PERIOD = 30

@dataclass
class CurrRates:
    id: str
    rates: list[Decimal]
    labels: list[str]
    min_rate: Decimal | None = None
    max_rate: Decimal | None = None
    last_rate: Decimal | None = None

    def get_info(self):
        color = [int(x) for x in CURR_COLOR[self.id.upper()].split(',')]
        return {
            'id': self.id,
            'rate': self.last_rate,
            'rates': self.rates,
            'color': {
                'r': color[0],
                'g': color[1],
                'b': color[2],
            },
        }

def get_db_currency_chart(period: ChartPeriod, base: str):
    enddate = datetime.today()
    startdate = get_start_date(enddate, period)

    rates_list: list[CurrRates] = []
    for curr in CURR_LIST:
        if curr == 'USD':
            continue
        rates = get_hist_exchange_rates(startdate.date(), enddate.date(), curr)
        src_data = []
        days = (enddate-startdate).days
        if not days:
            days = 1
        for i in range(days):
            sd = SourceData(event=startdate + timedelta(i), value=rates[i])
            src_data.append(sd)
        chart_points = approximate(src_data, 200)
        labels = [v['x'] for v in chart_points]
        rates: list[Decimal] = [v['y'] for v in chart_points]
        curr_rates = CurrRates(id=curr.lower(), rates=rates, labels=labels)
        rates_list.append(curr_rates)

    usd_rates = CurrRates(id='usd', rates=[], labels=[])
    if base != 'usd':
        filtered_rates = [x for x in rates_list if x.id == base]
        if filtered_rates:
            base_rates: CurrRates = filtered_rates[0]
            for i in range(len(base_rates.rates)):
                base_rate = base_rates.rates[i]
                if not base_rate:
                    base_rate = 1
                usd_rates.rates.append(Decimal(1 / base_rate))

                for curr_rates in rates_list:
                    if curr_rates.id == base:
                        continue
                    if i < len(curr_rates.rates):
                        tmp = curr_rates.rates[i]
                        curr_rates.rates[i] = Decimal(tmp * usd_rates.rates[i])
                    else:
                        curr_rates.rates.append(Decimal(0))

                base_rates.rates[i] = Decimal(1)
    rates_list.append(usd_rates)

    for curr_rates in rates_list:
        a = [x for x in curr_rates.rates if x]
        if len(a):
            curr_rates.min_rate = Decimal(min(a))
            curr_rates.max_rate = Decimal(max(a))
            curr_rates.last_rate = a[-1]

    chart_config = build_chart_config('Currency Rates', [], '')

    widget_data = {
        'chart': chart_config,
        'base': base,
        'period': period.value,
        'labels': rates_list[0].labels,
        'currencies': [x.get_info() for x in rates_list],
    }
    return widget_data

def get_api_currency_chart(period: ChartPeriod, base: str):
    api_url = os.environ.get('DJANGO_HOST_LOG', '')
    service_token = os.environ.get('DJANGO_SERVICE_TOKEN', '')
    headers = {'Authorization': 'Token ' + service_token, 'User-Agent': 'Mozilla/5.0'}
    verify = os.environ.get('DJANGO_CERT', '')
    resp = requests.get(api_url + '/api/get_chart_data/?mark=currency&period=' + period.value + '&base=' + base, headers=headers, verify=verify)
    if (resp.status_code != 200):
        return None
    return json.loads(resp.content)

def get_currency_data(period: ChartPeriod, base: str):
    if os.environ.get('DJANGO_DEVICE', 'Nuc') != os.environ.get('DJANGO_LOG_DEVICE', 'Nuc'):
        ret = get_api_currency_chart(period, base)
        if ret:
            return ret
    return get_db_currency_chart(period, base)
