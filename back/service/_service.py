"""Background process

A regular call to the API method that provides the operation of various site services.
"""
import os, sys, requests, time, json, traceback
from dataclasses import dataclass
from enum import Enum

DJANGO_CERT = os.environ.get('DJANGO_CERT')
MODULE_DIR = os.path.dirname(os.path.abspath(DJANGO_CERT)) + '\\'
sys.path.append(os.path.dirname(MODULE_DIR))
from logs.logger import get_logger, set_app, use_file, set_service
logger = get_logger(__name__, local_only=True)
LOGS_PATH = os.environ.get('DJANGO_LOG_BASE', '')
use_file(logger, LOGS_PATH + '\\cron.log')
set_app(logger, 'cron')
set_service(logger, 'worker')

class ApiCallStatus(Enum):
    started = 'started'
    connected = 'connected'
    disconnected = 'disconnected'
    error = 'error'
    debug = 'debug'

@dataclass
class ApiCallState:
    status: ApiCallStatus
    message: str


@dataclass(frozen=True)
class Params:
    this_server = os.environ.get('DJANGO_DEVICE', '???')
    api_host: str = os.environ.get('DJANGO_HOST_API', '')
    verify: str = os.environ.get('DJANGO_CERT', '')
    api_url: str = api_host + '/api/tasks/check_background_services/?format=json'
    service_token: str = os.environ.get('DJANGO_SERVICE_TOKEN', '')
    timer_interval_sec: int = int(os.environ.get('DJANGO_SERVICE_INTERVAL_SEC', 60))

    def headers(self):
        return {'Authorization': 'Token ' + self.service_token, 'User-Agent': 'Mozilla/5.0'}


def change_connection_status(params: Params, api_state: ApiCallState, new_status: ApiCallStatus):
    if new_status == ApiCallStatus.connected:
        method = logger.info
    else:
        method = logger.warning
    method(f'{api_state.status.value}->{new_status.value}')
    api_state.status = new_status


""" API call
"""
def call_api(params: Params, api_state: ApiCallState):
    extra_param = ''
    if api_state.status == ApiCallStatus.started:
        extra_param = '&started=true'
    url = params.api_url + extra_param
    resp = None
    status = api_state.status
    message = ''
    try:
        resp = requests.get(url, headers=params.headers(), verify=params.verify)
        if status == ApiCallStatus.started or status == ApiCallStatus.disconnected:
            change_connection_status(params, api_state, ApiCallStatus.connected)
    except requests.exceptions.ConnectionError as ex:
        if status != ApiCallStatus.disconnected:
            change_connection_status(params, api_state, ApiCallStatus.disconnected)
    except Exception as ex:
        status = ApiCallStatus.error
        logger.exception(ex)
        message = traceback.format_exc()

    if status == ApiCallStatus.connected:
        if not resp or not resp.status_code:
            status = ApiCallStatus.error
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
                message = f'{params.api_host} API server returned status {resp.status_code}. {message}.'
            else:
                data_str = resp.json()
                data = json.loads(data_str)
                if ('result' not in data):
                    status = ApiCallStatus.error
                    message = f'{params.api_host} API call: Unexpected API response. Attribute "result" not found: ' + data_str
                else:
                    if data['result'] != 'ok':
                        status = ApiCallStatus.error
                        message = data_str

        api_state.status = status
        api_state.message = message

if (__name__ == '__main__'):
    params = Params()
    api_state = ApiCallState(status=ApiCallStatus.started, message='')

    try:
        while True:
            logger.debug(api_state.status.value)
            call_api(params, api_state)

            if api_state.status == ApiCallStatus.error:
                logger.error(api_state.status.value + ': ' + api_state.message)

            time.sleep(params.timer_interval_sec)
    except Exception as ex:
        logger.exception(ex)
