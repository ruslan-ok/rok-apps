from datetime import date
from core.currency.custom_api.exchange_rate_api import ExchangeRateApi
from core.models import CurrencyRate


class UnimplementedApi(ExchangeRateApi):

    def __init__(self, api_id: str):
        self.api_id = api_id
        super().__init()

    def _get_rate_on_date(self, date: date, currency: str, base: str='USD') -> tuple[CurrencyRate|None, str|None]:
        return None, 'Undefined exchange rate update API ' + self.api_id

