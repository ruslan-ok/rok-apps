"""Background process

A regular call to the API method that provides the operation of various site services.
"""
import os, requests, time, smtplib, json
from datetime import datetime
from email.message import EmailMessage
from dataclasses import dataclass
from enum import Enum

class ApiCallStatus(Enum):
    ok = 'ok'
    warning = 'warning'
    error = 'error'
    exception = 'exception'

@dataclass(frozen=True)
class Params:
    host: str = os.environ.get('DJANGO_HOST', '')
    api_host: str = os.environ.get('DJANGO_HOST_API', '')
    verify: str = os.environ.get('DJANGO_CERT', '')
    mail_host: str = os.environ.get('DJANGO_HOST_MAIL', '')
    user: str = os.environ.get('DJANGO_MAIL_USER', '')
    pwrd: str = os.environ.get('DJANGO_MAIL_PWRD', '')
    recipients: str = os.environ.get('DJANGO_MAIL_ADMIN', '')
    api_url: str = api_host + '/api/tasks/check_background_services/?format=json'
    service_token: str = os.environ.get('DJANGO_SERVICE_TOKEN', '')
    timer_interval_sec: int = int(os.environ.get('DJANGO_SERVICE_INTERVAL_SEC', 60))

    def headers(self):
        return {'Authorization': 'Token ' + self.service_token, 'User-Agent': 'Mozilla/5.0'}

""" Notification that do not require email
"""
def console_log(status: str, message: str=''):
    print(f'{datetime.now():%Y.%m.%d %H:%M} {status}')
    if message:
        print(message)

""" Email notification
"""
def notify(params: Params, status: ApiCallStatus, subject: str, message: str, format: str='plain'):
    if params.host == 'localhost' and format != 'html':
        console_log(str(status), message)
    s = smtplib.SMTP(host=params.mail_host, port=25)
    s.starttls()
    s.login(params.user, params.pwrd)
    msg = EmailMessage()
    msg['From'] = params.user
    msg['To'] = params.recipients
    msg['Subject'] = subject

    if format == 'plain':
        msg.set_content(f'Background process for host {params.host} (/service/_service.py):\n\n' + message)
    else:
        msg.set_content(message, maintype='text', subtype=format)
    s.send_message(msg)
    del msg
    s.quit()

""" API call
"""
def call_api(params, started):
    extra_param = ''
    if started:
        extra_param = '&started=true'
    resp = None
    status:ApiCallStatus = ApiCallStatus.ok
    subject = None
    message = ''
    format = 'plain'
    try:
        resp = requests.get(params.api_url + extra_param, headers=params.headers(), verify=params.verify)
    except Exception as ex:
        status = ApiCallStatus.exception
        message = str(ex)
        subject = f'API server {params.api_host} is not available.'

    if not resp or not resp.status_code:
        if params.host == 'localhost':
            status = ApiCallStatus.warning
        else:
            status = ApiCallStatus.error
        message = f'API server {params.api_host} is not available.'
    else:
        if (resp.status_code != 200):
            status = ApiCallStatus.error
            try:
                message = resp.content.decode()
            except (UnicodeDecodeError, AttributeError):
                message = str(resp.content)
            message = f'{resp.status_code=}. {message}'
        else:
            data_str = resp.json()
            data = json.loads(data_str)
            if ('result' not in data):
                status = ApiCallStatus.error
                message = 'Unexpected API response. Attribute "result" not found: ' + data_str
            else:
                if data['result'] != 'ok':
                    status = ApiCallStatus.error
                    message = data_str

    if '<html' in message:
        format = 'html'

    if not subject:
        subject = f'Background service notification. {status=}'

    return status, subject, message, format

if (__name__ == '__main__'):
    params = Params()
    started = True
    try:
        while True:
            if started:
                console_log('started')
            else:
                console_log('work')

            status, subject, message, format = call_api(params, started)

            if status != ApiCallStatus.ok:
                if status == ApiCallStatus.warning:
                    console_log(str(status), message)
                else:
                    notify(params, status, subject, message, format)

            if started:
                started = False

            time.sleep(params.timer_interval_sec)
    except Exception as ex:
        notify(params, ApiCallStatus.exception, 'Background service interrupted', str(ex))