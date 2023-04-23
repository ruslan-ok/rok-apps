"""Site service manager
"""
import os, json, traceback
from datetime import datetime, date
from logs.models import ServiceEvent, EventType
from backup.backuper import Backuper
from task.const import APP_SERVICE, ROLE_MANAGER
from todo.notificator import Notificator
from fuel.serv_interval import ServInterval
from logs.log_analyzer import LogAnalyzer
from task.models import Group, Task
from rusel.settings import ENV, DB

def log_event(name, type=EventType.INFO, info=None):
    device = os.environ.get('DJANGO_DEVICE')
    event = ServiceEvent.objects.create(device=device, app=APP_SERVICE, service=ROLE_MANAGER, type=type, name=name, info=info)
    if name == 'work':
        ServiceEvent.objects.filter(device=device, app=APP_SERVICE, service=ROLE_MANAGER, type=EventType.INFO, name=name, created__date=date.today()).exclude(id=event.id).delete()

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
        case _: service = None
    if not service:
        log_event('process', info=f'Service with name "{service_class}" not found. Task "{service_task.name}".', type=EventType.WARNING)
        return False
    is_ripe, completed = service.ripe()
    if not is_ripe:
        return completed
    try:
        log_event('process', info=service.service_descr)
        completed = service.process()
        log_event('process_completed', info=str(completed))
        return completed
    except:
        log_event('exception', info=f'Exception {traceback.format_exc()}', type=EventType.ERROR)
        return False

def _check_services(started):
    log_event('start' if started else 'work')
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
        log_event('exception', info=f'in _check_services(): {ex}', type=EventType.ERROR)
        ret = json.dumps(ret_dict)
    return ret