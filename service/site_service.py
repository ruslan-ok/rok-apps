"""Site service interface

The base behavior of the site service.
"""
import os, smtplib, requests, json
from datetime import datetime, timedelta
from email.message import EmailMessage
from logs.models import ServiceEvent, EventType
from task.const import APP_SERVICE, ROLE_MANAGER

class SiteService():
    template_name = 'logs'

    def __init__(self, app, service_name, service_descr=None, device=None, local_log=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        this_device = os.environ.get('DJANGO_DEVICE')
        if device:
            self.device = device
        else:
            self.device = this_device
        self.app = app
        self.service_name = service_name
        self.service_descr = service_descr
        self.mail_host = os.environ.get('DJANGO_HOST_MAIL')
        self.user = os.environ.get('DJANGO_MAIL_USER')
        self.pwrd = os.environ.get('DJANGO_MAIL_PWRD')
        self.recipients = os.environ.get('DJANGO_MAIL_ADMIN')
        self.use_log_api = (this_device != 'Nuc')
        self.local_log = local_log
        api_host = os.environ.get('DJANGO_HOST_LOG')
        #api_host = 'http://localhost:8000'
        self.api_url = f'{api_host}/en/api/logs/?format=json'
        service_token = os.environ.get('DJANGO_SERVICE_TOKEN')
        self.headers = {'Authorization': 'Token ' + service_token, 'User-Agent': 'Mozilla/5.0'}
        self.verify = os.environ.get('DJANGO_CERT')

    def get_extra_context(self, request):
        context = {}
        day=None
        if 'day' in request.GET:
            day = request.GET['day']
        context['events'] = self.get_events(device=self.device, app=self.app, service=self.service_name, day=day)
        return context

    def ripe(self):
        return False
        
    def process(self):
        return datetime.now() + timedelta(hours=1)

    def log_event(self, type, name, info=None, send_mail=False, one_per_day=False):
        if self.use_log_api and not self.local_log:
            self.log_event_api(type, name, info, one_per_day)
        else:
            event = ServiceEvent.objects.create(device=self.device, app=self.app, service=self.service_name, type=type, name=name, info=info)
            if one_per_day:
                ServiceEvent.objects.filter(device=self.device, app=self.app, service=self.service_name, type=type, name=name, info=info).exclude(id=event.id).delete()
        if send_mail:
            s = smtplib.SMTP(host=self.mail_host, port=25)
            s.starttls()
            s.login(self.user, self.pwrd)
            msg = EmailMessage()
            if self.service_descr:
                msg['From'] = self.service_descr + '<' + self.user + '>'
            else:
                msg['From'] = self.user
            msg['To'] = self.recipients
            match type:
                case 'error': prefix = 'x'
                case 'warning': prefix = '!'
                case _: prefix = 'i'
            msg['Subject']='Service Event: [' + prefix + ']' + name
            if info:
                msg.set_content(info)
            else:
                msg.set_content(name)
            s.send_message(msg)
            del msg
            s.quit()

    def log_event_api(self, type, name, info, one_per_day):
        data = {
            'device': self.device,
            'app': self.app,
            'service': self.service_name,
            'type': str(type),
            'name': name,
            'info': info,
            'one_per_day': str(one_per_day)
        }
        resp = requests.post(self.api_url, headers=self.headers, verify=self.verify, json=data)
        if (resp.status_code != 201):
            ServiceEvent.objects.create(device=self.device, app=APP_SERVICE, service=ROLE_MANAGER, type=EventType.ERROR, name='log_api_post', info='[x] error ' + str(resp.status_code) + '. ' + str(resp.content))
 
    def get_events(self, device=None, app=None, service=None, type=None, name=None, day=None, order_by=None, local_log=None):
        if not order_by:
            order_by = '-created'

        if local_log == None:
            local_log = self.local_log
        
        if not device:
            device = self.device

        if self.use_log_api and not local_log:
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

    def get_events_api(self, device, app, service, type, name, day, order_by):
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
            ServiceEvent.objects.create(device=self.device, app=APP_SERVICE, service=ROLE_MANAGER, type=EventType.ERROR, name='log_api_get', info='[x] error ' + str(resp.status_code) + '. ' + str(resp.content))
            return []
        ret = json.loads(resp.content)
        ret2 = [EventFromApi(x) for x in ret['results']]
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
