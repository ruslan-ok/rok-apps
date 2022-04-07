"""Checking for the appearance of tasks that need to be reminded. Generating of reminder messages.

Exported functions:
-------------------
ripe()
process(log)
"""
from datetime import datetime
import firebase_admin, sys, requests, json
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError
from secret import cred_cert, service_user_token, certfile_path

HOST_PROD = 'https://rusel.by'
HOST_DEV = 'http://localhost:8000'
HOST = HOST_DEV

TASK_API_RIPE      = HOST + '/api/tasks/reminder_ripe/?format=json'
TASK_API_PROCESS   = HOST + '/api/tasks/reminder_process/?format=json'
TASK_API_TOKENS    = HOST + '/api/tasks/get_tokens/?format=json&user_id={}'
TASK_API_DEL_TOKEN = HOST + '/api/tasks/del_token/?format=json&user_id={}&token={}'
TASK_API_REMINDED  = HOST + '/api/tasks/reminded/?format=json&task_id={}'
headers = {'Authorization': 'Token ' + service_user_token, 'User-Agent': 'Mozilla/5.0'}
verify = certfile_path
exc_pref = '[x] process() [service/todo.py] '

def ripe(log):
    """Are there any tasks that need to be reminded.
    
    Returns
    ----------
    True if any.
    """
    #log('headers: ' + json.dumps(headers))
    #log('verify: ' + verify)
    resp = requests.get(TASK_API_RIPE, headers=headers, verify=verify)
    #log('resp: ' + resp.text)
    data = resp.json()
    if ('result' in data):
        return data['result']
    #log('todo.py: ripe(): ' + json.dumps(data))
    return False

def process(log):
    """Generating of reminder messages.
    
    Parameters
    ----------
    log: method
        Method for logging processed data.
    """
    try:
        resp = requests.get(TASK_API_PROCESS, headers=headers, verify=verify)
        resp.raise_for_status()
        data = resp.json()
        if ('result' not in data):
            return
        for task in data['result']:
            remind_one_task(log, task)
    except requests.exceptions.HTTPError as errh:
        log(exc_pref + 'Http Error: ' + str(errh))
    except requests.exceptions.ConnectionError as errc:
        log(exc_pref + 'Error Connecting: ' + str(errc))
    except requests.exceptions.Timeout as errt:
        log(exc_pref + 'Timeout Error: ' + str(errt))
    except requests.exceptions.RequestException as err:
        log(exc_pref + 'OOps: Something Else ' + str(err))

def remind_one_task(log, task):
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_cert)
        firebase_admin.initialize_app(cred)

    body = task['term'] + ' - ' + task['group']
    n = messaging.Notification(title=task['name'], body=body, image=None)
    if (task['important']):
        priority = 'high'
    else:
        priority = 'normal'
    myicon = HOST + '/static/rusel.png'
    mybadge = ''
    click_action = HOST + '/todo/' + str(task['id']) + '/'
    an = messaging.AndroidNotification(title=task['name'], body=body, icon=myicon, color=None, sound=None, tag=None, click_action=click_action, body_loc_key=None, \
                                       body_loc_args=None, title_loc_key=None, title_loc_args=None, channel_id=None, image=None, ticker=None, sticky=None, \
                                       event_timestamp=None, local_only=None, priority=None, vibrate_timings_millis=None, default_vibrate_timings=None, \
                                       default_sound=None, light_settings=None, default_light_settings=None, visibility=None, notification_count=None)
    messaging.AndroidConfig(collapse_key=None, priority=priority, ttl=None, restricted_package_name=None, data=None, notification=an, fcm_options=None)
    actions = []
    a1 = messaging.WebpushNotificationAction('postpone', 'Postpone 1 hour', icon=HOST+'/static/icons/postpone.png')
    a2 = messaging.WebpushNotificationAction('done', 'Done', icon=HOST+'/static/icons/completed.png')
    actions.append(a1)
    actions.append(a2)

    wn = messaging.WebpushNotification(title=task['name'], body=body, icon=myicon, badge=mybadge, actions=actions, tag=str(task['id']), custom_data={"click_action": click_action})
    messaging.WebpushFCMOptions(click_action)
    wc = messaging.WebpushConfig(headers=None, data=None, notification=wn, fcm_options=None)
    
    resp = requests.get(TASK_API_TOKENS.format(task['user_id']), headers=headers, verify=verify)
    data = resp.json()
    if ('result' not in data) or (len(data['result']) == 0):
        log('[TODO] No tokens for user_id = ' + str(task['user_id']))
        return
    tokens = data['result']
    
    mm = messaging.MulticastMessage(tokens=tokens, data=None, notification=n, android=None, webpush=wc, apns=None, fcm_options=None)
    r = messaging.send_multicast(mm, dry_run=False, app=None)
    ret_resp = '[' + str(len(r.responses)) + ']'
    log('[TODO] Remind task ID: {}, ok: {}, err: {}, resp: {}, name: "{}"'.format(task['id'], r.success_count, r.failure_count, ret_resp, task['name']))
    npp = 1
    for z in r.responses:
        if z.success:
            status = 'Success'
            error_desc = ''
        else:
            status = 'Fail'
            error_desc = ', ' + z.exception.code
        msg = ''
        if z.message_id:
            msg += ', message_id = "' + z.message_id + '"'
        log('       {}. {}{}{}'.format(npp, status, error_desc, msg))
        log('       token "' + tokens[npp-1] + '"')
        if (not z.success) and (z.exception.code == 'NOT_FOUND'):
            resp = requests.get(TASK_API_DEL_TOKEN.format(task['user_id'], tokens[npp-1]), headers=headers, verify=verify)
            data = resp.json()
            if ('result' not in data) and data['result']:
                log('       [!] Token deleted.')
        npp += 1

    requests.get(TASK_API_REMINDED.format(task['id']), headers=headers, verify=verify)

