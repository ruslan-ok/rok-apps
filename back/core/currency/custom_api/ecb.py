import io
import pandas as pd
from decimal import Decimal
from core.currency.custom_api.exchange_rate_api import ExchangeRateApi
from core.models import CurrencyRate


class ECB(ExchangeRateApi):
    
    def __init__(self):
        super().__init__('ecb.europa.eu')
        self.headers.update({'Accept': 'text/csv'})

    def _process_resp(self, date, resp) -> CurrencyRate:
        df = pd.read_csv(io.StringIO(resp.text))
        s_value = df['OBS_VALUE']
        value = round(Decimal(s_value.values[0]), 6)
        if not self.inverse:
            value = 1 / value
        rate = self.store_rate(date, self.currency, self.base, 1, value)
        return rate
