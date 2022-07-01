import requests
from secret import service_user_token, certfile_path

HOST_PROD = 'https://rusel.by'
HOST_DEV = 'http://localhost:8000'
HOST = HOST_PROD
TASK_API_FUEL_CHECK = HOST + '/api/tasks/check_service_intervals/?format=json'
headers = {'Authorization': 'Token ' + service_user_token, 'User-Agent': 'Mozilla/5.0'}
verify = certfile_path
exc_pref = '[x] process() [fuel.py] '

def process(log):
    """Daily check of service intervals.
    """
    log('Daily check of service intervals...')
    resp = requests.get(TASK_API_FUEL_CHECK, headers=headers, verify=verify)
    data = resp.json()
    if ('result' in data):
        log('Daily check of service intervals: ' + data['result'])
        return True
    log(exc_pref + 'There is no "result" in the response.')
    return False
