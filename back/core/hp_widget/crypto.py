import os, requests, json
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from core.hp_widget.delta import approximate, ChartPeriod, SourceData, build_chart_config

def get_crypto_data(period: ChartPeriod):
    chart_points = []
    current = change = amount = None
    api_url = settings.API_COIN_RATE
    api_key = settings.API_COIN_RATE_KEY
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
                chart_points = approximate(src_data, 200)

    chart_config = build_chart_config('BTC/USD', chart_points, '111, 184, 71')
    widget_data = {
        'chart': chart_config,
        'current': current,
        'change': change,
        'amount': amount,
        'price_url': settings.API_COIN_INFO, 
        'amount_url': f"{settings.API_WALLET}{settings.API_WALLET_KEY}",
    }
    return widget_data
