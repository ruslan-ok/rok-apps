import json
from datetime import datetime
from core.currency.custom_api.exchange_rate_api import ExchangeRateApi
from core.models import CurrencyRate


class NBP(ExchangeRateApi):
    
    def __init__(self):
        super().__init__('api.nbp.pl')

    def _process_resp(self, date, resp) -> CurrencyRate:
        resp_json = json.loads(resp.content)
        if len(resp_json) != 1:
            raise Exception('api.resp_json parsing error')
        api_date = datetime.strptime(resp_json[0]['effectiveDate'], '%Y-%m-%d')
        filtered = [x for x in resp_json[0]['rates'] if x['code'] in ('USD', 'EUR', 'GBP')]
        ret = None
        for x in filtered:
            currency_rate = self.store_rate(api_date, self.base, x['code'], 1, x['mid'])
            if x['code'] == 'USD':
                ret = currency_rate
        return ret
