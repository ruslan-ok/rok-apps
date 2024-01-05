"""Site cron listener
"""
import os, json, traceback
from datetime import datetime
from backup.backuper import Backuper
from todo.notificator import Notificator
from fuel.serv_interval import ServInterval
from logs.log_analyzer import LogAnalyzer
from core.currency.exchange_rate_service import ExchangeRate
from task.models import Group, Task
from rusel.settings import ENV, DB
from logs.logger import get_logger


logger = get_logger(__name__, 'cron', 'worker', True)


def process_service(service_task):
    service_class = service_task.categories
    match service_class:
        case 'Backuper':
            service = Backuper(service_task)
        case 'Notificator':
            service = Notificator()
        case 'ServInterval':
            service = ServInterval()
        case 'Apache':
            service = LogAnalyzer(service_task)
        case 'ExchangeRate':
            service = ExchangeRate()
        case _: service = None
    if not service:
        logger.warning(f'Service with name "{service_class}" not found. Task "{service_task.name}".')
        return False
    is_ripe, completed = service.ripe()
    if not is_ripe:
        return completed
    try:
        logger.info(service.service_descr + '|started')
        completed = service.process()
        logger.info(service.service_descr + '|finished ' + str(completed))
        return completed
    except:
        logger.exception(f'Exception {traceback.format_exc()}')
        return False

def _check_services(started):
    if started:
        logger.info('start')
    else:
        logger.info({'one_per_day': True, 'message': 'work'})
    svc_grp = int(os.environ.get('DJANGO_SERVICE_GROUP' + ENV + DB))
    grp = Group.objects.filter(id=svc_grp).get()
    services = Task.objects.filter(groups=grp, completed=False)
    now = datetime.now()
    for service_task in services:
        if not service_task.stop or service_task.stop <= now:
            completed = process_service(service_task)
            if completed and service_task.stop and (service_task.repeat != 0):
                service_task.toggle_completed()
    ret = {'result': 'ok'}
    return json.dumps(ret)
    
def check_services(started):
    try:
        ret = _check_services(started)
    except:
        ex = traceback.format_exc()
        ret_dict = {'result': 'error', 'exception': ex}
        logger.exception(f'in _check_services(): {ex}')
        ret = json.dumps(ret_dict)
    return ret