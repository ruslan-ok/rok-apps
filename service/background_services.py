"""Site service manager
"""
import os, json
from datetime import datetime
from task.models import ServiceEvent
from backup.backuper import Backuper
from todo.notificator import Notificator
from fuel.serv_interval import ServInterval
from logs.log_analyzer import LogAnalyzer
from task.models import Group, Task

def log_event(name, type='info', info=None):
    event = ServiceEvent.objects.create(app='service', service='manager', type=type, name=name, info=info)
    if name == 'call':
        ServiceEvent.objects.filter(app='service', service='manager', type='info', name=name).exclude(id=event.id).delete()

def process_service(service_class):
    match service_class:
        case 'backup.backuper.Backuper':
            service = Backuper()
        case 'todo.notificator.Notificator':
            service = Notificator()
        case 'fuel.serv_interval.ServInterval':
            service = ServInterval()
        case 'logs.log_analyzer.LogAnalyzer':
            service = LogAnalyzer()
        case _: service = None
    if not service or not service.ripe():
        return False
    try:
        log_event('process', info=service.service_descr)
        completed = service.process()
        return completed
    except Exception as ex:
        log_event(f'Exception {str(ex)}', 'error')
        return False

def check_services(started):
    log_event('start' if started else 'call')
    svc_grp = int(os.environ.get('DJANGO_SERVICE_GROUP'))
    grp = Group.objects.filter(id=svc_grp).get()
    services = Task.objects.filter(groups=grp, completed=False)
    for service_task in services:
        if not service_task.stop or service_task.stop <= datetime.now():
            completed = process_service(service_task.info)
            if completed and service_task.stop and (service_task.repeat != 0):
                service_task.toggle_completed()
    ret = {'result': 'ok'}
    return json.dumps(ret)