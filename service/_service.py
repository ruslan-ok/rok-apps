"""Background process

A regular call to the API method that provides the operation of various site services.
"""
import os, requests, time, smtplib, json, traceback
from datetime import datetime
from email.message import EmailMessage
from dataclasses import dataclass
from enum import Enum

class ApiCallStatus(Enum):
    ok = 'ok'
    warning = 'warning'
    error = 'error'
    exception = 'exception'
    started = 'started'
    work = 'work'

@dataclass(frozen=True)
class Params:
    host: str = os.environ.get('DJANGO_HOST', '')
    api_host: str = os.environ.get('DJANGO_HOST_API', '')
    verify: str = '' # os.environ.get('DJANGO_CERT', '')
    mail_host: str = os.environ.get('DJANGO_HOST_MAIL', '')
    user: str = os.environ.get('DJANGO_MAIL_USER', '')
    pwrd: str = os.environ.get('DJANGO_MAIL_PWRD', '')
    recipients: str = os.environ.get('DJANGO_MAIL_ADMIN', '')
    api_url: str = api_host + '/api/tasks/check_background_services/?format=json'
    service_token: str = os.environ.get('DJANGO_SERVICE_TOKEN', '')
    timer_interval_sec: int = int(os.environ.get('DJANGO_SERVICE_INTERVAL_SEC', 60))
    log_base: str = os.environ.get('DJANGO_LOG_BASE', '')

    def headers(self):
        return {'Authorization': 'Token ' + self.service_token, 'User-Agent': 'Mozilla/5.0'}

""" Notification that do not require email
"""
def console_log(log_base: str, status: ApiCallStatus=ApiCallStatus.ok, message: str=''):
    now = datetime.now()
    log_path = log_base + now.strftime('\\%Y\\%m')
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    fname = now.strftime('%d_service.log')
    log_row = f'{now:%H:%M} [{status.value}] {message}'
    with open(log_path + '\\' + fname, 'a', encoding='utf-8') as f:
        f.write(log_row + '\n')
    print(log_row)

""" Email notification
"""
def notify(params: Params, status: ApiCallStatus, subject: str, message: str, format: str='plain'):
    if params.host == 'localhost' and format != 'html':
        console_log(params.log_base, status, message)
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
    resp = requests.get(params.api_url + extra_param, headers=params.headers(), verify=params.verify)

    if not resp or not resp.status_code:
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
                console_log(params.log_base, ApiCallStatus.started)
            else:
                console_log(params.log_base, ApiCallStatus.work)

            status, subject, message, format = call_api(params, started)

            if status != ApiCallStatus.ok:
                if status == ApiCallStatus.warning:
                    console_log(params.log_base, status, message)
                else:
                    notify(params, status, subject, message, format)

            if started:
                started = False

            time.sleep(params.timer_interval_sec)
    except:
        console_log(params.log_base, ApiCallStatus.exception, traceback.format_exc())
        notify(params, ApiCallStatus.exception, 'Background service interrupted', traceback.format_exc())
