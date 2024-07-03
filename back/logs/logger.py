from datetime import date
import logging, requests, json
from logging import handlers
from django.conf import settings
try:
    from logs.models import ServiceEvent
    db_available = True
except:
    db_available = False
pass

class CustomHandler():
    app = None
    service = None

    def prepare(self, record):
        device = settings.DJANGO_DEVICE
        app = self.app if self.app else record.name.split('.')[0]
        service = self.service if self.service else record.module
        event_type = record.levelname.lower()
        if type(record.msg) == dict:
            name = record.msg.get('name', '----')
            message = record.msg.get('message', '')
            one_per_day = record.msg.get('one_per_day', False)
            info_dict = record.msg
            if not message:
                message = info_dict
        else:
            name = '----'
            message = str(record.msg)
            one_per_day = False
            info_dict = None
        details_dict = {
            'info_dict': info_dict,
            'func_name': record.funcName,
            'msecs': record.msecs,
            'name': record.name,
            'module': record.module,
            'pathname': record.pathname.replace('\\', '/'),
            'filename': record.filename,
            'lineno': record.lineno,
            'exc_info': record.exc_info,
            'exc_text': record.exc_text,
            'stack_info': record.stack_info,
            'process': record.process,
            'process_name': record.processName,
            'server_time': record.server_time if hasattr(record, 'server_time') else '',
            'thread': record.thread,
            'thread_name': record.threadName,
        }
        if details_dict['exc_info']:
            details_dict['exc_info'] = None
        data = {
            'device': device,
            'app': app,
            'service': service,
            'type': event_type,
            'name': name,
            'info': message,
            'details': details_dict,
            'one_per_day': one_per_day,
        }
        return data

    def emit(self, record):
        return record


class DatabaseHandler(logging.Handler, CustomHandler):

    def emit(self, record):
        data = self.prepare(record)
        info = data['info']
        if type(info) == dict:
            info = json.dumps(info)
        details = data['details']
        if type(details) == dict:
            details = json.dumps(details)
        event = ServiceEvent.objects.create(
            device=data['device'],
            app=data['app'],
            service=data['service'],
            type=data['type'],
            name=data['name'],
            info=info,
            details=details,
        )
        if data['one_per_day']:
            ServiceEvent.objects.filter(
                device=data['device'],
                app=data['app'],
                service=data['service'],
                type=data['type'],
                name=data['name'],
                info=info,
                created__date=date.today(),
            ).exclude(id=event.id).delete()
        return record


class ApiHandler(logging.Handler, CustomHandler):

    def __init__(self, local_only: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if local_only:
            api_host = settings.DJANGO_HOST_API
        else:
            api_host = settings.DJANGO_HOST_LOG
        if api_host.startswith('https://'):
            self.verify = settings.DJANGO_CERT
        else:
            self.verify = None
        self.api_url = f'{api_host}/api/logs?format=json'
        service_token = settings.DJANGO_SERVICE_TOKEN
        self.request_headers = {'Authorization': 'Token ' + service_token, 'User-Agent': 'Mozilla/5.0'}

    def emit(self, record):
        data = self.prepare(record)
        if type(data['info']) == dict:
            data['info'] = json.dumps(data['info'])
        if type(data['details']) == dict:
            data['details'] = json.dumps(data['details'])
        requests.post(self.api_url, headers=self.request_headers, verify=self.verify, json=data)
        return record


class MailHandler(handlers.SMTPHandler, CustomHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getSubject(self, record):
        data = self.prepare(record)
        name = ''
        if data["name"] != '----':
            name = f'.{data["name"]}'
        return f'ROK-APPS.COM: {data["device"]}.{data["app"]}.{data["service"]}{name}'


def get_logger(name: str, app: str=None, service: str=None, local_only: bool=False, file: str=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    console_formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s | %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    this_device = settings.DJANGO_DEVICE
    log_device = settings.DJANGO_LOG_DEVICE
    if db_available and (local_only or (this_device == log_device)):
        api_handler = DatabaseHandler()
    else:
        api_handler = ApiHandler(local_only)
    api_formatter = logging.Formatter(fmt='%(message)s')
    api_handler.setFormatter(api_formatter)
    logger.addHandler(api_handler)

    mail_formatter = logging.Formatter(fmt='%(levelname)s\n%(pathname)s:%(lineno)d\n\n%(message)s')
    host = settings.DJANGO_HOST_MAIL
    admin = settings.DJANGO_MAIL_ADMIN
    user = settings.DJANGO_MAIL_USER
    pwrd = settings.DJANGO_MAIL_PWRD
    mail_handler = MailHandler(
        mailhost=host,
        fromaddr=user,
        toaddrs=[admin],
        subject=host.upper(),
        credentials=(user, pwrd),
    )
    mail_handler.setFormatter(mail_formatter)
    mail_handler.setLevel(logging.WARNING)
    logger.addHandler(mail_handler)

    if app:
        set_app(logger, app)

    if service:
        set_service(logger, service)

    if file:
        logs_path = settings.DJANGO_LOG_BASE
        use_file(logger, logs_path + '\\' + file)

    return logger


def set_app(logger, app: str):
    for handler in logger.handlers:
        try:
            handler.app = app
        except:
            pass

def set_service(logger, service: str):
    for handler in logger.handlers:
        try:
            handler.service = service
        except:
            pass

def use_file(logger, filename):
    file_formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s | %(message)s')
    file_handler = handlers.TimedRotatingFileHandler(filename=filename, when='D',)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
