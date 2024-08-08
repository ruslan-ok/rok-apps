import requests, json
from datetime import date
from prefect import flow
from exchange_rate_update_params import (
    rate_api,
    headers,
    verify
)

CURRENCY_API = {
    'EUR': 'ecb',
    'PLN': 'nbp',
    'BYN': 'myfin',
    'GBP': 'boe',
}

@flow(flow_run_name='Curremcy update for {currency} using API {api_name}', log_prints=True)
def check_exchange_rate(currency: str, api_name: str, days: list[str]):
    this_day = date.today().strftime('%a')
    if this_day not in days:
        print('Skipping {this_day}')
        return
    resp = requests.get(f'{rate_api}?currency={currency}&api_name={api_name}', headers=headers, verify=verify)
    if (resp.status_code != 200):
        print('[ERROR] api_call: Status = ' + str(resp.status_code) + '. ' + str(resp.content))
    else:
        ret = json.loads(resp.content)
        print(f'[Ok] {ret}')

if __name__ == '__main__':
    for currency, api_name in CURRENCY_API.items():
        check_exchange_rate(currency, api_name, ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])

