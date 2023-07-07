"""Background process

A regular call to the API method that provides the operation of various site services.
"""
import os, requests, time, smtplib, json, traceback
from datetime import datetime
from email.message import EmailMessage
from dataclasses import dataclass
from enum import Enum

class ApiCallStatus(Enum):
    started = 'started'
    connected = 'connected'
    disconnected = 'disconnected'
    error = 'error'
    debug = 'debug'

@dataclass
class ApiCallState:
    status: ApiCallStatus
    subject: str
    message: str
    format: str


@dataclass(frozen=True)
class Params:
    this_server = os.environ.get('DJANGO_DEVICE', '???')
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
    log_base: str = os.environ.get('DJANGO_LOG_BASE', '')
    con_subject_template = '{} connection: {}->{}'
    con_message_template = 'A background service (/service/_service.py) on the {} server changed the connection status to the {} server from {} to {}.'

    def headers(self):
        return {'Authorization': 'Token ' + self.service_token, 'User-Agent': 'Mozilla/5.0'}


def change_connection_status(params: Params, api_state: ApiCallState, new_status: ApiCallStatus):
    subject = params.con_subject_template.format(params.this_server, api_state.status.value, new_status.value)
    message = params.con_message_template.format(params.this_server, params.api_host, api_state.status.value, new_status.value)
    notify(params, api_state.status, subject, message)
    api_state.status = new_status


""" Notification that do not require email
"""
def console_log(log_base: str, status: ApiCallStatus, message: str=''):
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

    if format == 'plain' and api_state.status == ApiCallStatus.error:
        msg.set_content(f'Background process for host {params.host} (/service/_service.py):\n\n' + message)
    elif format == 'plain':
        msg.set_content(message)
    else:
        msg.set_content(message, maintype='text', subtype=format)
    s.send_message(msg)
    del msg
    s.quit()

""" API call
"""
def call_api(params: Params, api_state: ApiCallState):
    extra_param = ''
    if api_state.status == ApiCallStatus.started:
        extra_param = '&started=true'
    url = params.api_url + extra_param
    resp = None
    status = api_state.status
    subject = ''
    message = ''
    format = 'plain'
    try:
        resp = requests.get(url, headers=params.headers(), verify=params.verify)
        if status == ApiCallStatus.started or status == ApiCallStatus.disconnected:
            change_connection_status(params, api_state, ApiCallStatus.connected)
    except requests.exceptions.ConnectionError as ex:
        if status != ApiCallStatus.disconnected:
            change_connection_status(params, api_state, ApiCallStatus.disconnected)
    except:
        status = ApiCallStatus.error
        subject = f'{params.this_server} API call: exception'
        message = traceback.format_exc()

    if status == ApiCallStatus.connected:
        if not resp or not resp.status_code:
            status = ApiCallStatus.error
            subject = f'{params.this_server} API call: empty responce'
            resp_status_code = None
            if resp:
                resp_status_code = resp.status_code
            message = f'{params.api_host} API server returned empty responce.\n{resp=}\n{resp_status_code=}\nCalled to {url}'
        else:
            if (resp.status_code != 200):
                status = ApiCallStatus.error
                try:
                    message = resp.content.decode()
                except (UnicodeDecodeError, AttributeError):
                    message = str(resp.content)
                subject = f'{params.this_server} API call: {resp.status_code}'
                message = f'{params.api_host} API server returned status {resp.status_code}. {message}.'
            else:
                data_str = resp.json()
                data = json.loads(data_str)
                if ('result' not in data):
                    status = ApiCallStatus.error
                    subject = f'{params.this_server} API call: bad response'
                    message = f'{params.api_host} API call: Unexpected API response. Attribute "result" not found: ' + data_str
                else:
                    if data['result'] != 'ok':
                        status = ApiCallStatus.error
                        subject = f'{params.this_server} API call: bad result'
                        message = data_str

        if '<html' in message:
            format = 'html'

        api_state.status = status
        api_state.subject = subject
        api_state.message = message
        api_state.format = format

if (__name__ == '__main__'):
    params = Params()
    api_state = ApiCallState(status=ApiCallStatus.started, subject='', message='', format='plain')

    try:
        while True:
            console_log(params.log_base, api_state.status)
            call_api(params, api_state)

            if api_state.status == ApiCallStatus.error:
                console_log(params.log_base, api_state.status, api_state.message)
                notify(params, api_state.status, api_state.subject, api_state.message, api_state.format)

            time.sleep(params.timer_interval_sec)
    except:
        message = traceback.format_exc()
        console_log(params.log_base, ApiCallStatus.error, message)
        notify(params, ApiCallStatus.error, f'{params.this_server} exception', message)
