"""Site service interface

The base behavior of the site service.
"""
import os, smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from task.models import ServiceEvent

class SiteService():

    def __init__(self, app, service_name, service_descr=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        self.service_name = service_name
        self.service_descr = service_descr
        self.mail_host = os.environ.get('DJANGO_HOST_MAIL')
        self.user = os.environ.get('DJANGO_MAIL_USER')
        self.pwrd = os.environ.get('DJANGO_MAIL_PWRD')
        self.recipients = os.environ.get('DJANGO_MAIL_ADMIN')

    def ripe(self):
        return False
        
    def process(self):
        return datetime.now() + timedelta(hours=1)

    def log_event(self, type, name, info=None, send_mail=False):
        ServiceEvent.objects.create(app=self.app, service=self.service_name, type=type, name=name, info=info)
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

