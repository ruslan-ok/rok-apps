"""Site service manager
"""
import os, json
from datetime import datetime, date
from logs.models import ServiceEvent, EventType
from backup.backuper import BackupNucShort, BackupNucFull, BackupVivoShort, BackupVivoFull
from todo.notificator import Notificator
from fuel.serv_interval import ServInterval
from logs.log_analyzer import LogAnalyzer
from task.models import Group, Task

def log_event(name, type=EventType.INFO, info=None):
    device = os.environ.get('DJANGO_DEVICE')
    event = ServiceEvent.objects.create(device=device, app='service', service='manager', type=type, name=name, info=info)
    if name == 'work':
        ServiceEvent.objects.filter(device=device, app='service', service='manager', type=EventType.INFO, name=name, created__date=date.today()).exclude(id=event.id).delete()

def process_service(service_name, service_class):
    match service_class:
        case 'backup.backuper.BackupNucShort':
            service = BackupNucShort()
        case 'backup.backuper.BackupNucFull':
            service = BackupNucFull()
        case 'backup.backuper.BackupVivoShort':
            service = BackupVivoShort()
        case 'backup.backuper.BackupVivoFull':
            service = BackupVivoFull()
        case 'todo.notificator.Notificator':
            service = Notificator()
        case 'fuel.serv_interval.ServInterval':
            service = ServInterval()
        case 'logs.log_analyzer.LogAnalyzer':
            service = LogAnalyzer()
        case _: service = None
    if not service or not service.ripe():
        if not service:
            log_event('process', info=f'Service with name "{service_class}" not found. Task "{service_name}".', type=EventType.WARNING)
        return False
    try:
        log_event('process', info=service.service_descr)
        completed = service.process()
        return completed
    except Exception as ex:
        log_event('exception', info=f'Exception {str(ex)}', type=EventType.ERROR)
        return False

def _check_services(started):
    log_event('start' if started else 'work')
    svc_grp = int(os.environ.get('DJANGO_SERVICE_GROUP'))
    grp = Group.objects.filter(id=svc_grp).get()
    services = Task.objects.filter(groups=grp, completed=False)
    now = datetime.now()
    for service_task in services:
        if not service_task.stop or service_task.stop <= now:
            completed = process_service(service_task.name, service_task.info)
            if completed and service_task.stop and (service_task.repeat != 0):
                service_task.toggle_completed()
    ret = {'result': 'ok'}
    return json.dumps(ret)
    
def check_services(started):
    ret = {'result': 'error'}
    try:
        ret = _check_services(started)
    except Exception as ex:
        log_event('exception', info=f'in _check_services(): {str(ex)}', type=EventType.ERROR)
    return ret