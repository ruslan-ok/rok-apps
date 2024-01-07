from datetime import datetime
from service.site_service import SiteService
from core.currency.utils import get_exchange_rate_for_api
from logs.logger import get_logger


logger = get_logger(__name__, 'currency', 'exchange_rate')


CURRENCY_API = {
    'EUR': 'ecb',
    'PLN': 'nbp',
    'BYN': 'myfin',
    #'BYN': 'nbrb',
    'GBP': 'boe',
}

class ExchangeRate(SiteService):

    def __init__(self, service_task, *args, **kwargs):
        self.params = service_task.info.split('\r\n')
        super().__init__('Обновление курсов валют', *args, **kwargs)

    def ripe(self):
        return True, True

    def process(self):
        logger.info(f'+process({', '.join(self.params)})')
        for currency, api_name in CURRENCY_API.items():
            if self.params and currency not in self.params:
                continue
            rate, info = get_exchange_rate_for_api(datetime.today().date(), currency, 'USD', api_name, skip_db='yes')
            if rate:
                logger.info({
                    'currency': currency,
                    'rate_api': api_name,
                    'rate': str(rate),
                    'info': info,
                })
            else:
                logger.warning({
                    'currency': currency,
                    'rate_api': api_name,
                    'info': info,
                })
        logger.info('-process()')
        return True
