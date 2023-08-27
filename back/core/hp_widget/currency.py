import os, json, requests
from datetime import date, datetime, timedelta
from dataclasses import dataclass
from decimal import Decimal
from core.currency.utils import get_exchange_rate, get_hist_exchange_rates
from core.currency.exchange_rate_api import CA_Status
from core.hp_widget.delta import get_start_date, approximate, ChartPeriod, ChartDataVersion, SourceData

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

def get_currency(request):
    currencies = []
    for curr in CURR_LIST:
        if curr == 'USD':
            continue
        rate_info = get_exchange_rate(curr, datetime.today().date())
        if rate_info and rate_info.result == CA_Status.ok and rate_info.rate and rate_info.rate.value:
            currencies.append({
                'icon': CURR_ICON[curr], 
                'abbr': CURR_ABBR[curr], 
                'style': f'{curr.lower()}-rate', 
                'rate': round(rate_info.rate.value, 2),
                'date': rate_info.rate.date,
                'code': curr,
            })
    context = {
        'currencies': currencies,
        'copyright_url': os.getenv('API_NBRB_CR_URL', '#'),
        'copyright_info': os.getenv('API_NBRB_CR_INFO', ''), 
    }
    template_name = 'hp_widget/currency.html'
    return template_name, context

@dataclass
class CurrRates:
    id: str
    rates: list[Decimal]
    labels: list[str]
    min_rate: Decimal | None = None
    max_rate: Decimal | None = None
    last_rate: Decimal | None = None

    def get_info_v1(self):
        values = []
        if self.max_rate and self.min_rate and (self.max_rate > self.min_rate):
            delta: Decimal = self.max_rate - self.min_rate
            for i in range(len(self.labels)):
                values.append({
                    'x': self.labels[i],
                    'y': (self.rates[i]-self.min_rate)/delta if self.rates[i] else self.rates[i]
                })
        return {
            'label': self.id.upper(),
            'data': values,
            'backgroundColor': f'rgba({CURR_COLOR[self.id.upper()]}, 0.2)',
            'borderColor': f'rgba({CURR_COLOR[self.id.upper()]}, 1)',
            'borderWidth': 1,
            'tension': 0.4,
        }
    
    def get_info_v2(self):
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

def get_db_currency_chart(user_id: int, period: ChartPeriod, version: ChartDataVersion, base: str):
    enddate = datetime.today()
    startdate = get_start_date(enddate, period)

    rates_list: list[CurrRates] = []
    for curr in CURR_LIST:
        if curr == 'USD':
            continue
        rates = get_hist_exchange_rates(curr, startdate.date(), enddate.date())
        src_data = []
        days = (enddate-startdate).days
        if not days:
            days = 1
        for i in range(days):
            sd = SourceData(event=startdate + timedelta(i), value=rates[i])
            src_data.append(sd)
        values = approximate(period, src_data, 200)
        labels = [v['x'] for v in values]
        rates: list[Decimal] = [v['y'] for v in values]
        curr_rates = CurrRates(id=curr.lower(), rates=rates, labels=labels)
        rates_list.append(curr_rates)

    usd_rates = CurrRates(id='usd', rates=[], labels=[])
    if base != 'usd':
        base_rates: CurrRates = [x for x in rates_list if x.id == base][0]
        for i in range(len(base_rates.rates)):
            base_rate = base_rates.rates[i]
            if not base_rate:
                base_rate = 1
            usd_rates.rates.append(Decimal(1 / base_rate))

            for curr_rates in rates_list:
                if curr_rates.id == base:
                    continue
                tmp = curr_rates.rates[i]
                curr_rates.rates[i] = Decimal(tmp * usd_rates.rates[i])

            base_rates.rates[i] = Decimal(1)
    rates_list.append(usd_rates)

    for curr_rates in rates_list:
        a = [x for x in curr_rates.rates if x]
        if len(a):
            curr_rates.min_rate = Decimal(min(a))
            curr_rates.max_rate = Decimal(max(a))
            curr_rates.last_rate = a[-1]

    match version:
        case ChartDataVersion.v1:
            data = {
                'type': 'line',
                'data': {
                    'datasets': [x.get_info_v1() for x in rates_list]
                },
                'options': {
                    'plugins': {
                        'legend': {
                            'display': False,
                        },
                    },
                    'elements': {
                        'point': {
                            'radius': 0,
                        },
                    },
                },
            }

        case ChartDataVersion.v2:
            data = {
                'base': base,
                'period': period.value,
                'labels': rates_list[0].labels,
                'currencies': [x.get_info_v2() for x in rates_list],
            }
        case _: data = {}
    return data

def get_api_currency_chart(period: ChartPeriod, version: ChartDataVersion, base: str):
    api_url = os.environ.get('DJANGO_HOST_LOG', '')
    service_token = os.environ.get('DJANGO_SERVICE_TOKEN', '')
    headers = {'Authorization': 'Token ' + service_token, 'User-Agent': 'Mozilla/5.0'}
    verify = os.environ.get('DJANGO_CERT', '')
    resp = requests.get(api_url + '/api/get_chart_data/?mark=currency&version=' + version.value + '&period=' + period.value + '&base=' + base, headers=headers, verify=verify)
    if (resp.status_code != 200):
        return None
    return json.loads(resp.content)

def get_chart_data(user_id: int, period: ChartPeriod, version: ChartDataVersion, base: str):
    if os.environ.get('DJANGO_DEVICE', 'Nuc') != os.environ.get('DJANGO_LOG_DEVICE', 'Nuc'):
        ret = get_api_currency_chart(period, version, base)
        if ret:
            return ret
    return get_db_currency_chart(user_id, period, version, base)
