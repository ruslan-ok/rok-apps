from core.currency.custom_api.exchange_rate_api import ExchangeRateApi


class CurrencyApi(ExchangeRateApi):
    
    def __init__(self):
        super().__init__('currencyapi.com')

