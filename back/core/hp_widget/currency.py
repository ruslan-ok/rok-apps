import os
from datetime import datetime, timedelta
from task.models import Task
from task.const import NUM_ROLE_EXPENSE, NUM_ROLE_FUEL, NUM_ROLE_APART, NUM_ROLE_SERV_VALUE
from apart.models import Apart, ServiceAmount
from core.currency.utils import get_exchange_rate, get_hist_exchange_rates
from core.currency.exchange_rate_api import *
from core.hp_widget.delta import get_start_date, approximate, ChartPeriod, ChartDataVersion, SourceData

#CURR_LIST = ('PLN', 'BYN')
CURR_LIST = ('EUR', 'BYN', 'PLN', 'GBP')

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
        if not currency_used(request.user.id, curr):
            continue
        rate_info = get_exchange_rate(curr, datetime.today().date())
        if rate_info and rate_info.result == CA_Status.ok and rate_info.rate:
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

def get_db_currency_chart(user_id: int, period: ChartPeriod, version: ChartDataVersion):
    enddate = datetime.today()
    startdate = get_start_date(enddate, period)

    currencies = []
    currencies.append({
        'id': 'usd',
        'code': 'USD',
        'currentRate': 1,
        'color': {
            'r': 1,
            'g': 2,
            'b': 3,
        }
    })
    datasets = []
    for curr in CURR_LIST:
        if not currency_used(user_id, curr):
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
        a = [x for x in rates if x]
        if len(a):
            min_rate = Decimal(min(a))
            max_rate = Decimal(max(a))
            if version == ChartDataVersion.v1:
                values = [(item['y']-min_rate)/(max_rate-min_rate) if item['y'] else item['y'] for item in values]
            if version == ChartDataVersion.v2:
                rate = 1
                if len(values):
                    rate = values[-1]['y']
                color = [int(x) for x in CURR_COLOR[curr].split(',')]
                currencies.append({
                    'id': curr.lower(),
                    'code': curr,
                    'currentRate': rate,
                    'color': {
                        'r': color[0],
                        'g': color[1],
                        'b': color[2],
                    },
                })
                datasets.append({
                    'currencyId': curr.lower(),
                    'rates': values,
                })
            else:
                datasets.append({
                    'label': curr,
                    'data': values,
                    'backgroundColor': f'rgba({CURR_COLOR[curr]}, 0.2)',
                    'borderColor': f'rgba({CURR_COLOR[curr]}, 1)',
                    'borderWidth': 1,
                    'tension': 0.4,
                    })

    if version == ChartDataVersion.v2:
        return {
            'baseId': 'usd',
            'periodId': period.value,
            'currencyList': currencies,
            'rates': datasets,
        }
    else:
        date = startdate
        x = []
        while date <= enddate:
            x.append(date.strftime('%m.%d'))
            date = date + timedelta(1)
        data = {
            'type': 'line',
            'data': {'labels': x,
                'datasets': datasets
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
        return data

def get_api_currency_chart(period: ChartPeriod, version: ChartDataVersion):
    api_url = os.environ.get('DJANGO_HOST_LOG', '')
    service_token = os.environ.get('DJANGO_SERVICE_TOKEN', '')
    headers = {'Authorization': 'Token ' + service_token, 'User-Agent': 'Mozilla/5.0'}
    verify = os.environ.get('DJANGO_CERT', '')
    resp = requests.get(api_url + '/api/get_chart_data/?mark=currency&version=' + version.value + '&period=' + period.value, headers=headers, verify=verify)
    if (resp.status_code != 200):
        return None
    return json.loads(resp.content)

def get_chart_data(user_id: int, period: ChartPeriod, version: ChartDataVersion):
    if os.environ.get('DJANGO_DEVICE', 'Nuc') != os.environ.get('DJANGO_LOG_DEVICE', 'Nuc'):
        ret = get_api_currency_chart(period, version)
        if ret:
            return ret
    return get_db_currency_chart(user_id, period, version)

def currency_used(user_id, currency):
    return True
    # if Task.objects.filter(user=user_id, app_expen=NUM_ROLE_EXPENSE, price_unit=currency, event__gt=(datetime.now()-timedelta(PERIOD))).exists():
    #     return True
    # if Task.objects.filter(user=user_id, app_fuel=NUM_ROLE_FUEL, price_unit=currency, event__gt=(datetime.now()-timedelta(PERIOD))).exists():
    #     return True
    # for apart in Apart.objects.filter(user=user_id, app_apart=NUM_ROLE_APART, price_unit=currency):
    #     if ServiceAmount.objects.filter(user=user_id, app_apart=NUM_ROLE_SERV_VALUE, task_1=apart.id, event__gt=(datetime.now()-timedelta(PERIOD))).exists():
    #         return True
    # return False
