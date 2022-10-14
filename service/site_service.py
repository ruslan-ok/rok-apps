"""Site service interface

The base behavior of the site service.
"""
import os, smtplib, requests
from datetime import datetime, timedelta
from email.message import EmailMessage
from logs.models import ServiceEvent, EventType
from task import const


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
        self.api_host = os.environ.get('DJANGO_HOST_LOG')
        self.api_url = f'{self.api_host}/en/api/logs/?format=json'
        service_token = os.environ.get('DJANGO_SERVICE_TOKEN')
        self.headers = {'Authorization': 'Token ' + service_token, 'User-Agent': 'Mozilla/5.0'}
        self.verify = os.environ.get('DJANGO_CERT')

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
            subject = 'Service Event: [' + prefix + ']' + name
            msg['Subject'] = subject
            if info:
                msg.set_content(info)
            else:
                msg.set_content(name)
            s.send_message(msg)
            del msg
            s.quit()
            ServiceEvent.objects.create(device=self.device, app=self.app, service=self.service_name, type=EventType, name='mail', 
                info=f'To:[{self.recipients}], Subject:"[{subject}], Body:[{info[:40]}...]')

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
            ServiceEvent.objects.create(device=self.device, app=const.APP_SERVICE, service=const.ROLE_MANAGER, type=EventType.ERROR, name='log_api_post', info='[x] error ' + str(resp.status_code) + '. ' + str(resp.content))
