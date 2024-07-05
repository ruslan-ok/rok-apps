import os, requests, json
from datetime import datetime

from django.conf import settings

from task import const
from logs.models import EventType, ServiceEvent

class ServiceLog():
    template_name = 'logs'

    def __init__(self, dev, app, svc):
        super().__init__()
        self.dev = dev
        self.app = app
        self.svc = svc
        self.local_log = False
        self.this_device = settings.DJANGO_DEVICE
        self.log_device = settings.DJANGO_LOG_DEVICE
        self.use_log_api = (self.this_device != self.log_device)
        if self.use_log_api and (app != 'cron' or svc != 'worker'):
            self.log_location = self.log_device
        else:
            self.log_location = self.this_device
        self.api_host = settings.DJANGO_HOST_LOG
        self.api_url = f'{self.api_host}/api/logs/?format=json'
        service_token = settings.DJANGO_SERVICE_TOKEN
        self.headers = {'Authorization': 'Token ' + service_token, 'User-Agent': 'Mozilla/5.0'}
        self.verify = settings.DJANGO_CERT

    def get_extra_context(self, request):
        context = {}
        day=None
        if 'day' in request.GET:
            day_str = request.GET['day']
            day = datetime.strptime(day_str, '%Y%m%d')
        context['events'] = self.get_events(device=self.dev, app=self.app, service=self.svc, day=day)
        context['icon'] = self.get_icon()
        context['title'] = self.get_descr()
        return context

    def get_sort(self):
        match (self.dev, self.app, self.svc):
            case (_,      'cron',     'worker'):      return 1
            case ('Nuc',  'backup',   'short'):       return 2
            case ('Nuc',  'backup',   'full'):        return 3
            case ('Vivo', 'backup',   'short'):       return 4
            case ('Vivo', 'backup',   'full'):        return 5
            case ('Nuc',  'todo',     'notificator'): return 6
            case ('Nuc',  'fuel',     'part'):        return 7
            case ('Nuc',  'logs',     'apache'):      return 8
            case ('Nuc',  'win-acme', 'copy_cert'):   return 9
            case ('Vivo', 'currency', 'exchange_rate'): return 10
            case ('Nuc',  'currency', 'exchange_rate'): return 11
            case _: return 99

    def get_icon(self):
        match (self.dev, self.app, self.svc):
            case (_,      'cron',     'worker'):      return 'fast-forward'
            case ('Nuc',  'backup',   'short'):       return 'save'
            case ('Nuc',  'backup',   'full'):        return 'save-fill'
            case ('Vivo', 'backup',   'short'):       return 'save'
            case ('Vivo', 'backup',   'full'):        return 'save-fill'
            case ('Nuc',  'todo',     'notificator'): return 'bell'
            case ('Nuc',  'fuel',     'part'):        return 'tools'
            case ('Nuc',  'logs',     'apache'):      return 'server'
            case ('Nuc',  'win-acme', 'copy_cert'):   return 'award'
            case ('Vivo', 'currency', 'exchange_rate'): return 'currency-dollar'
            case ('Nuc',  'currency', 'exchange_rate'): return 'currency-dollar'
            case _: return 'card-list'
    
    def get_href(self):
        return f'dev={self.dev}&app={self.app}&svc={self.svc}'
    
    def get_descr(self):
        match (self.dev, self.app, self.svc):
            case (_,      'cron',     'worker'):      return 'Cron worker'
            case ('Nuc',  'backup',   'short'):       return 'Backup Nuc short'
            case ('Nuc',  'backup',   'full'):        return 'Backup Nuc full'
            case ('Vivo', 'backup',   'short'):       return 'Backup Vivo short'
            case ('Vivo', 'backup',   'full'):        return 'Backup Vivo full'
            case ('Nuc',  'todo',     'notificator'): return 'Task Notificator'
            case ('Nuc',  'fuel',     'part'):        return 'Service intervals'
            case ('Nuc',  'logs',     'apache'):      return 'Apache log'
            case ('Nuc',  'win-acme', 'copy_cert'):   return 'Win-ACME'
            case ('Vivo', 'currency', 'exchange_rate'): return 'Vivo Exchange rate update'
            case ('Nuc',  'currency', 'exchange_rate'): return 'Nuc Exchange rate update'
            case _: return f'{self.dev} - {self.app} - {self.svc}'
 
    def get_events(self, device=None, app=None, service=None, type=None, name=None, day=None, order_by=None):
        if not order_by:
            order_by = '-created'

        if not device:
            device = self.dev

        if self.use_log_api and not self.local_log:
            return self.get_events_api(device, app, service, type, name, day, order_by)

        data = ServiceEvent.objects.filter(device=device).order_by(order_by, '-id')
        if app:
            data = data.filter(app=app)
        if service:
            data = data.filter(service=service)
        if type:
            data = data.filter(type=type)
        if name:
            data = data.filter(info=name)
        if day:
            data = data.filter(created__date=day)
        return data

    def get_events_api(self, device=None, app=None, service=None, type=None, name=None, day=None, order_by=None):
        if not order_by:
            order_by = '-created'

        extra_param = f'&device={device}&app={app}&service={service}'

        if type:
            extra_param += f'&type={str(type)}'
        if name:
            extra_param += f'&name={name}'
        if day:
            extra_param += f'&day={day.strftime("%Y%m%d")}'
        if order_by:
            extra_param += f'&order_by={order_by}'
        resp = requests.get(self.api_url + extra_param, headers=self.headers, verify=self.verify)
        if (resp.status_code != 200):
            ServiceEvent.objects.create(device=self.dev, app='cron', service='worker', type=EventType.ERROR, name='log_api_get', info='[x] error ' + str(resp.status_code) + '. ' + str(resp.content))
            return []
        ret = json.loads(resp.content)
        ret2 = [EventFromApi(x) for x in ret]
        return ret2
    
    def write(self, type: EventType, name: str, info: str):
        ServiceEvent.objects.create(device=self.dev, app=self.app, service=self.svc, type=type, name=name, info=info)

class EventFromApi():

    def __init__(self, resp, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = resp['id']
        self.device = resp['device']
        self.app = resp['app']
        self.service = resp['service']
        self.created = datetime.strptime(resp['created'], '%Y-%m-%dT%H:%M:%S.%f')
        self.type = EventType(resp['type'])
        self.name = resp['name']
        self.info = resp['info']

    def __repr__(self):
        return f'{self.app}:{self.service} [{self.created.strftime("%Y-%m-%d %H:%M:%S")}] {self.type} | {self.name} - {self.info}'
    
    def s_info(self):
        if self.info:
            return self.info
        return ''

    def type_color(self):
        match self.type:
            case EventType.ERROR: ret = 'red'
            case EventType.WARNING: ret = 'orange'
            case _: ret = 'black'
        return ret

    def type_bg_color(self):
        match self.type:
            case EventType.ERROR: ret = 'snow'
            case EventType.WARNING: ret = 'ivory'
            case _: ret = 'white'
        return ret
