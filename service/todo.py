"""Checking for the appearance of tasks that need to be reminded. Generating of reminder messages.

Exported functions:
-------------------
ripe()
process(log)
"""
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError
from db import DB
from secret import cred_cert

def ripe():
    """Are there any tasks that need to be reminded.
    
    Returns
    ----------
    True if any.
    """
    db = DB()
    db.open()
    params = (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),)
    ret = db.execute('SELECT COUNT(id) FROM %d.todo_task WHERE completed = FALSE AND remind IS NOT NULL AND remind < ?', params)
    db.close()
    return ret and ret[0] and ret[0][0] and (ret[0][0] > 0)

def process(log):
    """Generating of reminder messages.
    
    Parameters
    ----------
    log: method
        Method for logging processed data.
    """
    db = DB()
    db.open()
    params = (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),)
    ret = db.execute('SELECT id, user_id, name, important, remind FROM %d.todo_task WHERE completed = FALSE AND remind IS NOT NULL AND remind < ? ORDER BY remind', params)
    for x in ret:
        task = {}
        task['id'] = x[0]
        task['user_id'] = x[1]
        task['name'] = x[2]
        task['important'] = x[3]
        if (len(str(x[4])) == 19):
            task['remind'] = datetime.strptime(str(x[4]), '%Y-%m-%d %H:%M:%S')
        else:
            task['remind'] = datetime.strptime(str(x[4]), '%Y-%m-%d %H:%M:%S.%f')
        remind_one_task(log, db, task)
    db.close()

def remind_one_task(log, db, task):
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_cert)
        default_app = firebase_admin.initialize_app(cred)

    body = 'Remind time {}'.format(task['remind'].strftime('%H:%M'))
    n = messaging.Notification(title = task['name'], body = body, image = None)
    if (task['important'] != 0):
        priority = 'high'
    else:
        priority = 'normal'
    myicon = 'https://rusel.by/static/rok/img/test-192.png'
    mybadge = 'https://rusel.by/static/rok/img/test-72.png'
    click_action = 'https://rusel.by/todo/' + str(task['id']) + '/'
    an = messaging.AndroidNotification(title = task['name'], body = body, icon = myicon, color = None, sound = None, tag = None, click_action = click_action, body_loc_key = None, \
                                       body_loc_args = None, title_loc_key = None, title_loc_args = None, channel_id = None, image = None, ticker = None, sticky = None, \
                                       event_timestamp = None, local_only = None, priority = None, vibrate_timings_millis = None, default_vibrate_timings = None, \
                                       default_sound = None, light_settings = None, default_light_settings = None, visibility = None, notification_count = None)
    aс = messaging.AndroidConfig(collapse_key = None, priority = priority, ttl = None, restricted_package_name = None, data = None, notification = an, fcm_options = None)
    actions = []
    a1 = messaging.WebpushNotificationAction('postpone', 'Postpone', icon = 'https://rusel.by/static/v2/todo/icon/remind-today.png')
    a2 = messaging.WebpushNotificationAction('done', 'Done', icon = 'https://rusel.by/static/v2/rok/icon/delete.png')
    actions.append(a1)
    actions.append(a2)

    #wn = messaging.WebpushNotification(title = task.name, body = body, icon = icon, actions = actions, badge = None, data = None, direction = None, image = None, language = None, renotify = True, require_interaction = True, silent = False, tag = None, timestamp_millis = None, vibrate = None, custom_data = None)
    wn = messaging.WebpushNotification(title = task['name'], body = body, icon = myicon, badge = mybadge, actions = actions, tag = str(task['id']), custom_data = {"click_action": click_action})
    wo = messaging.WebpushFCMOptions(click_action)
    wc = messaging.WebpushConfig(headers = None, data = None, notification = wn, fcm_options = None)
    
    ret = db.execute('SELECT token FROM %d.todo_subscription WHERE user_id = ?', (task['user_id'],))
    tokens = []
    for x in ret:
        tokens.append(x[0])
    
    mm = messaging.MulticastMessage(tokens = tokens, data = None, notification = n, android = None, webpush = wc, apns = None, fcm_options = None)
    r = messaging.send_multicast(mm, dry_run = False, app = None)
    ret_resp = '[' + str(len(r.responses)) + ']: '
    npp = 0
    for z in r.responses:
        if (len(ret_resp) > 0):
            ret_resp += ', '
        if z.success:
            ret_resp += '1'
        else:
            ret_resp += '0 ' + z.exception.code
            if (z.exception.code == 'NOT_FOUND'):
                ss[npp].delete()
        npp += 1

        if z.message_id:
            ret_resp += ':' + z.message_id
    
    log('[TODO] Remind task ID: {}, ok: {}, err: {}, resp: {}, name: "{}"'.format(task['id'], r.success_count, r.failure_count, ret_resp, task['name']))

    db.execute('UPDATE %d.todo_task SET last_remind = ?, remind = NULL WHERE id = ?', (datetime.now(), task['id']))


