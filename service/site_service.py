"""Site service interface

The base behavior of the site service.
"""
import os, smtplib, requests
from datetime import datetime, timedelta
from email.message import EmailMessage
from logs.models import ServiceEvent

class SiteService():
    template_name = 'logs'

    def __init__(self, app, service_name, service_descr=None, local_log=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.service_name = service_name
        self.service_descr = service_descr
        self.mail_host = os.environ.get('DJANGO_HOST_MAIL')
        self.user = os.environ.get('DJANGO_MAIL_USER')
        self.pwrd = os.environ.get('DJANGO_MAIL_PWRD')
        self.recipients = os.environ.get('DJANGO_MAIL_ADMIN')
        self.device = os.environ.get('DJANGO_DEVICE')
        self.use_log_api = (self.device != 'Nuc')
        self.local_log = local_log

    def get_extra_context(self, request):
        context = {}
        day=None
        if 'day' in request.GET:
            day = request.GET['day']
        context['events'] = self.get_events(app=self.app, service=self.service_name, day=day)
        return context

    def ripe(self):
        return False
        
    def process(self):
        return datetime.now() + timedelta(hours=1)

    def log_event(self, type, name, info=None, send_mail=False):
        if self.use_log_api:
            self.log_event_api(type, name, info)
        else:
            ServiceEvent.objects.create(device=self.device, app=self.app, service=self.service_name, type=type, name=name, info=info)
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

    def log_event_api(self, type, name, info):
        api_host = os.environ.get('DJANGO_HOST_API')
        service_token = os.environ.get('DJANGO_SERVICE_TOKEN')
        verify = os.environ.get('DJANGO_CERT')
        api_url = f'{api_host}/en/api/logs/?format=json'
        headers = {'Authorization': 'Token ' + service_token, 'User-Agent': 'Mozilla/5.0'}
        data = {
            'device': self.device,
            'app': self.app,
            'service': self.service_name,
            'type': str(type),
            'name': name,
            'info': info,
        }
        resp = requests.post(api_url, headers=headers, verify=verify, json=data)
        if (resp.status_code != 201):
            ServiceEvent.objects.create(device=self.device, app='service', service='manager', type='error', name='log_api', info='[x] error ' + str(resp.status_code) + '. ' + resp.content)
 
    def get_events(self, app=None, service=None, type=None, name=None, day=None, order_by=None, local_log=None):
        if not order_by:
            order_by = '-created'

        if local_log == None:
            local_log = self.local_log

        if self.use_log_api and not local_log:
            return self.get_events_api(app, service, type, name, day, order_by)

        data = ServiceEvent.objects.filter(device=self.device).order_by(order_by)
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

    def get_events_api(self, app, service, type, name, day, order_by):
        return []
