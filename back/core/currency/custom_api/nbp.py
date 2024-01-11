from core.currency.custom_api.exchange_rate_api import ExchangeRateApi


class NBP(ExchangeRateApi):
    
    def __init__(self):
        super().__init__('api.nbp.pl')
