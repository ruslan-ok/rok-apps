import os, requests, json
from datetime import datetime, timedelta

def get_currency(request):
    rate_usd = 1.
    rate_eur = 1.
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    api_url = os.getenv('API_NBRB')
    if api_url:
        url = api_url + '%?ondate=' + datetime.today().strftime('%Y-%m-%d') + '&parammode=2'
        resp = requests.get(url.replace('%', 'USD'), headers=headers)
        if resp.status_code == 200:
            ret = json.loads(resp.content)
            rate_usd = float(ret['Cur_OfficialRate'])
        resp = requests.get(url.replace('%', 'EUR'), headers=headers)
        if resp.status_code == 200:
            ret = json.loads(resp.content)
            rate_eur = float(ret['Cur_OfficialRate'])
    context = {
        'usd_rate_url': os.getenv('API_NBRB_STAT', '#'), 
        'eur_rate_url': os.getenv('API_NBRB_STAT', '#'),
        'usd_rate_value': f'USD {rate_usd:,.2f}',
        'eur_rate_value': f'EUR {rate_eur:,.2f}',
    }
    template_name = 'hp_widget/currency.html'
    return template_name, context

def get_chart_data(user_id: int):
    x = []
    usd = []
    eur = []
    startdate = datetime.today() - timedelta(30)
    enddate = datetime.today()
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    api_url = os.getenv('API_NBRB')
    if api_url:
        url = api_url + 'dynamics/%?startdate=' + startdate.strftime('%Y-%m-%d') + '&enddate=' + enddate.strftime('%Y-%m-%d')
        resp = requests.get(url.replace('%', '431'), headers=headers)
        if resp.status_code == 200:
            ret = json.loads(resp.content)
            for rate in ret:
                x.append(datetime.strptime(rate['Date'], '%Y-%m-%dT%H:%M:%S').date().strftime('%m.%d'))
                usd.append(float(rate['Cur_OfficialRate']))
        resp = requests.get(url.replace('%', '451'), headers=headers)
        if resp.status_code == 200:
            ret = json.loads(resp.content)
            for rate in ret:
                eur.append(float(rate['Cur_OfficialRate']))
    data = {
        'type': 'line',
        'data': {'labels': x,
            'datasets': [{
                'label': 'USD',
                'data': usd,
                'backgroundColor': 'rgba(111, 184, 71, 0.2)',
                'borderColor': 'rgba(111, 184, 71, 1)',
                'borderWidth': 1,
                'tension': 0.4,
            },
            {
                'label': 'EUR',
                'data': eur,
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1,
                'tension': 0.4,
            }]
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
