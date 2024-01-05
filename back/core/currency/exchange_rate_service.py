from datetime import date, datetime, timedelta
from service.site_service import SiteService
from core.currency.utils import get_exchange_rate_for_api
from logs.logger import get_logger


logger = get_logger(__name__, 'currency', 'exchange_rate')


CURRENCY_API = {
    'EUR': 'ecb',
    'PLN': 'nbp',
    'BYN': 'nbrb',
    'GBP': 'boe',
}

class ExchangeRate(SiteService):

    def __init__(self, *args, **kwargs):
        super().__init__('Обновление курсов валют', *args, **kwargs)

    def ripe(self):
        return True, True

    def process(self):
        logger.info('+process()')
        for currency, api_name in CURRENCY_API.items():
            rate, info = get_exchange_rate_for_api(datetime.today().date(), currency, 'USD', api_name)
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
