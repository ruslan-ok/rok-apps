import os, requests, json
from datetime import datetime, timedelta
from task.models import Task
from task.const import NUM_ROLE_EXPENSE, NUM_ROLE_FUEL

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
    'PLN': 'bi-currency-yen',
    'BYN': 'bi-currency-rupee',
    'GBP': 'bi-currency-pound',
}

PERIOD = 30

def get_currency(request):
    currencies = []
    for curr in CURR_LIST:
        if not currency_used(request.user.id, curr):
            continue
        rate_info = Task.get_exchange_rate(curr, datetime.today())
        if rate_info and 'rate' in rate_info and rate_info['rate']:
            icon = 'bi-currency-dollar'
            currencies.append({
                'icon': CURR_ICON[curr], 
                'style': f'{curr.lower()}-rate', 
                'rate': rate_info['rate'].value, 
                'date': rate_info['rate'].date,
                'code': curr,
            })
    context = {
        'currencies': currencies,
        'copyright_url': os.getenv('API_NBRB_CR_URL', '#'),
        'copyright_info': os.getenv('API_NBRB_CR_INFO', ''), 
    }
    template_name = 'hp_widget/currency.html'
    return template_name, context

def get_chart_data(user_id: int):
    enddate = datetime.today().date()
    startdate = enddate - timedelta(PERIOD)
    date = startdate
    x = []
    while date <= enddate:
        x.append(date.strftime('%m.%d'))
        date = date + timedelta(1)
    data = {
        'type': 'line',
        'data': {'labels': x,
            'datasets': []
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
    for curr in CURR_LIST:
        if not currency_used(user_id, curr):
            continue
        rates = Task.get_hist_exchange_rates(curr, startdate, enddate)
        a = [x for x in rates if x]
        min_rate = min(a)
        max_rate = max(a)
        rates = [(x-min_rate)/(max_rate-min_rate) if x else x for x in rates]
        data['data']['datasets'].append({
            'label': curr,
            'data': rates,
            'backgroundColor': f'rgba({CURR_COLOR[curr]}, 0.2)',
            'borderColor': f'rgba({CURR_COLOR[curr]}, 1)',
            'borderWidth': 1,
            'tension': 0.4,
            })
    return data

def currency_used(user_id, currency):
    ret = False
    if Task.objects.filter(user=user_id, app_expen=NUM_ROLE_EXPENSE, price_unit=currency, event__gt=(datetime.now()-timedelta(PERIOD))).exists():
        ret = True
    elif Task.objects.filter(user=user_id, app_fuel=NUM_ROLE_FUEL, price_unit=currency, event__gt=(datetime.now()-timedelta(PERIOD))).exists():
        ret = True
    return ret
