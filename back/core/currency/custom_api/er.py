from core.currency.custom_api.exchange_rate_api import ExchangeRateApi


class ExchangeRateHost(ExchangeRateApi):
    
    def __init__(self):
        super().__init__('api.exchangerate.host')
