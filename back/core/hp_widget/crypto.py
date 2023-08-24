import os, requests, json
from datetime import datetime
from decimal import Decimal
from core.hp_widget.delta import approximate, ChartPeriod, ChartDataVersion, SourceData

def get_crypto(request):
    price = 0.
    api_url = os.getenv('API_COIN_RATE')
    api_key = os.getenv('API_COIN_RATE_KEY')
    if api_url and api_key:
        headers = {'x-access-token': api_key, 'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(api_url + 'price', headers=headers)
        if resp.status_code == 200:
            ret = json.loads(resp.content)
            if ret['status'] == 'success':
                price = float(ret['data']['price'])
    context = {
        'crypto_price_url': os.getenv('API_COIN_INFO', '#'), 
        'crypto_amount_url': f"{os.getenv('API_WALLET', '#')}{os.getenv('API_WALLET_KEY', '')}",
        'crypto_price_value': f'${price:,.0f}',
        'crypto_amount_value': f'${0.07767845 * price:,.0f}',
        'copyright_url': os.getenv('API_COIN_CR_URL', '#'),
        'copyright_info': os.getenv('API_COIN_CR_INFO', ''), 
    }
    template_name = 'hp_widget/crypto.html'
    return template_name, context

def get_chart_data(period: ChartPeriod, version: ChartDataVersion):
    values = []
    current = change = amount = None
    api_url = os.getenv('API_COIN_RATE')
    api_key = os.getenv('API_COIN_RATE_KEY')
    if api_url and api_key:
        headers = {'x-access-token': api_key, 'User-Agent': 'Mozilla/5.0'}
        # timePeriod: 1h 3h 12h 24h 7d 30d 3m 1y 3y 5y
        resp = requests.get(api_url + 'history?timePeriod=' + period.value, headers=headers)
        if resp.status_code == 200:
            ret = json.loads(resp.content)
            if ret['status'] == 'success':
                current = float(ret['data']['history'][0]['price'])
                change = float(ret['data']['change'])
                amount = 0.07767845 * current
                src_data = []
                for i in reversed(range(len(ret['data']['history']))):
                    h = ret['data']['history'][i]
                    sd = SourceData(event=datetime.utcfromtimestamp(h['timestamp']), value=Decimal(h['price'] if h['price'] else 0))
                    src_data.append(sd)
                values = approximate(period, src_data, 200)

    if version == ChartDataVersion.v2:
        data = {
            'data': values,
            'current': current,
            'change': change,
            'amount': amount,
            'price_url': os.getenv('API_COIN_INFO', '#'), 
            'amount_url': f"{os.getenv('API_WALLET', '#')}{os.getenv('API_WALLET_KEY', '')}",
        }
    else:
        data = {
            'type': 'line',
            'data': {
                'datasets': [{
                    'label': 'BTC',
                    'data': values,
                    'backgroundColor': 'rgba(111, 184, 71, 0.2)',
                    'borderColor': 'rgba(111, 184, 71, 1)',
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
