import os
from datetime import datetime, timedelta
from task.models import Task
from task.const import NUM_ROLE_EXPENSE, NUM_ROLE_FUEL, NUM_ROLE_APART, NUM_ROLE_SERV_VALUE
from apart.models import Apart, ServiceAmount
from core.currency.utils import get_exchange_rate, get_hist_exchange_rates
from core.currency.exchange_rate_api import *

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
        rates = get_hist_exchange_rates(curr, startdate, enddate)
        a = [x for x in rates if x]
        if len(a):
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
    if Task.objects.filter(user=user_id, app_expen=NUM_ROLE_EXPENSE, price_unit=currency, event__gt=(datetime.now()-timedelta(PERIOD))).exists():
        return True
    if Task.objects.filter(user=user_id, app_fuel=NUM_ROLE_FUEL, price_unit=currency, event__gt=(datetime.now()-timedelta(PERIOD))).exists():
        return True
    for apart in Apart.objects.filter(user=user_id, app_apart=NUM_ROLE_APART, price_unit=currency):
        if ServiceAmount.objects.filter(user=user_id, app_apart=NUM_ROLE_SERV_VALUE, task_1=apart.id, event__gt=(datetime.now()-timedelta(PERIOD))).exists():
            return True
    return False
