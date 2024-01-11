from core.currency.custom_api.exchange_rate_api import ExchangeRateApi
from core.currency.custom_api.unimplemented_api import UnimplementedApi
from core.currency.custom_api.ecb import ECB
from core.currency.custom_api.nbp import NBP
from core.currency.custom_api.belta import Belta
from core.currency.custom_api.myfin import Myfin
from core.currency.custom_api.boe import BOE
from core.currency.custom_api.er import ExchangeRateHost
from core.currency.custom_api.ca import CurrencyApi


class ExchangeRateApiFactory:

    def get_api(self, api_id) -> ExchangeRateApi:
        match api_id:
            case 'ecb':   api = ECB()
            case 'nbp':   api = NBP()
            case 'belta': api = Belta()
            case 'myfin': api = Myfin()
            case 'boe':   api = BOE()
            case 'er':    api = ExchangeRateHost()
            case 'ca':    api = CurrencyApi()
            case _:       api = UnimplementedApi()
        return api
