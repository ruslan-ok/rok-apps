import os, requests, json
from datetime import datetime
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
        this_device = os.environ.get('DJANGO_DEVICE', '')
        self.use_log_api = (this_device != 'Nuc')
        self.api_host = os.environ.get('DJANGO_HOST_LOG', '')
        self.api_url = f'{self.api_host}/en/api/logs/?format=json'
        service_token = os.environ.get('DJANGO_SERVICE_TOKEN', '')
        self.headers = {'Authorization': 'Token ' + service_token, 'User-Agent': 'Mozilla/5.0'}
        self.verify = os.environ.get('DJANGO_CERT')

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
            case (_, const.APP_SERVICE, const.ROLE_MANAGER): return 1
            case ('Nuc',  const.APP_BACKUP,  const.ROLE_BACKUP_SHORT): return 2
            case ('Nuc',  const.APP_BACKUP,  const.ROLE_BACKUP_FULL): return 3
            case ('Vivo', const.APP_BACKUP,  const.ROLE_BACKUP_SHORT): return 4
            case ('Vivo', const.APP_BACKUP,  const.ROLE_BACKUP_FULL): return 5
            case ('Nuc',  const.APP_TODO,    const.ROLE_NOTIFICATOR): return 6
            case ('Nuc',  const.APP_FUEL,    const.ROLE_PART): return 7
            case ('Nuc',  const.APP_LOGS,    const.ROLE_APACHE): return 8
            case ('Nuc',  const.APP_W_ACME,  const.ROLE_CERT_COPY): return 9
            case _: return 99

    def get_icon(self):
        match (self.dev, self.app, self.svc):
            case (_, const.APP_SERVICE, const.ROLE_MANAGER): return 'fast-forward'
            case ('Nuc',  const.APP_BACKUP,  const.ROLE_BACKUP_SHORT): return 'save'
            case ('Nuc',  const.APP_BACKUP,  const.ROLE_BACKUP_FULL): return 'save-fill'
            case ('Vivo', const.APP_BACKUP,  const.ROLE_BACKUP_SHORT): return 'save'
            case ('Vivo', const.APP_BACKUP,  const.ROLE_BACKUP_FULL): return 'save-fill'
            case ('Nuc',  const.APP_TODO,    const.ROLE_NOTIFICATOR): return 'bell'
            case ('Nuc',  const.APP_FUEL,    const.ROLE_PART): return 'tools'
            case ('Nuc',  const.APP_LOGS,    const.ROLE_APACHE): return 'server'
            case ('Nuc',  const.APP_W_ACME,  const.ROLE_CERT_COPY): return 'award'
            case _: return 'card-list'
    
    def get_href(self):
        return f'dev={self.dev}&app={self.app}&svc={self.svc}'
    
    def get_descr(self):
        match (self.dev, self.app, self.svc):
            case (_, const.APP_SERVICE, const.ROLE_MANAGER): return 'Service manager'
            case ('Nuc',  const.APP_BACKUP,  const.ROLE_BACKUP_SHORT): return 'Backup Nuc short'
            case ('Nuc',  const.APP_BACKUP,  const.ROLE_BACKUP_FULL): return 'Backup Nuc full'
            case ('Vivo', const.APP_BACKUP,  const.ROLE_BACKUP_SHORT): return 'Backup Vivo short'
            case ('Vivo', const.APP_BACKUP,  const.ROLE_BACKUP_FULL): return 'Backup Vivo full'
            case ('Nuc',  const.APP_TODO,    const.ROLE_NOTIFICATOR): return 'Task Notificator'
            case ('Nuc',  const.APP_FUEL,    const.ROLE_PART): return 'Service intervals'
            case ('Nuc',  const.APP_LOGS,    const.ROLE_APACHE): return 'Apache log'
            case ('Nuc',  const.APP_W_ACME,  const.ROLE_CERT_COPY): return 'Win-ACME'
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
            data = data.filter(name=name)
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
            ServiceEvent.objects.create(device=self.device, app=const.APP_SERVICE, service=const.ROLE_MANAGER, type=EventType.ERROR, name='log_api_get', info='[x] error ' + str(resp.status_code) + '. ' + str(resp.content))
            return []
        ret = json.loads(resp.content)
        ret2 = [EventFromApi(x) for x in ret]
        return ret2    


class EventFromApi():

    def __init__(self, resp, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
