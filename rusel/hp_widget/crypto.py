import os, requests, json
from datetime import datetime

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

def get_chart_data(user_id: int):
    x = []
    y = []
    api_url = os.getenv('API_COIN_RATE')
    api_key = os.getenv('API_COIN_RATE_KEY')
    if api_url and api_key:
        headers = {'x-access-token': api_key, 'User-Agent': 'Mozilla/5.0'}
        # timePeriod: 1h 3h 12h 24h 7d 30d 3m 1y 3y 5y
        resp = requests.get(api_url + 'history?timePeriod=7d', headers=headers)
        if resp.status_code == 200:
            ret = json.loads(resp.content)
            if ret['status'] == 'success':
                for h in reversed(ret['data']['history']):
                    x.append(datetime.utcfromtimestamp(h['timestamp']).strftime('%m.%d'))
                    y.append(float(h['price']))

    data = {
        'type': 'line',
        'data': {'labels': x,
            'datasets': [{
                'label': 'BTC',
                'data': y,
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
