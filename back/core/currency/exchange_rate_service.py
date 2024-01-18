from datetime import datetime
from service.site_service import SiteService
from core.currency.utils import get_exchange_rate_for_api


CURRENCY_API = {
    'EUR': 'ecb',
    'PLN': 'nbp',
    'BYN': 'myfin',
    'GBP': 'boe',
}

class ExchangeRate(SiteService):

    def __init__(self, service_task, *args, **kwargs):
        self.params = service_task.info.split('\r\n')
        super().__init__('Обновление курсов валют', *args, **kwargs)

    def ripe(self):
        return True, True

    def process(self):
        for currency, api_name in CURRENCY_API.items():
            if self.params and currency not in self.params:
                continue
            get_exchange_rate_for_api(datetime.today().date(), currency, 'USD', api_name, mode='api_only_lad')
        return True
