"""Checking for the appearance of tasks that need to be reminded. Generating of reminder messages.

Exported functions:
-------------------
ripe()
process(log)
"""
from datetime import datetime, date
import firebase_admin, sys
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError
from secret import cred_cert

def ripe():
    """Are there any tasks that need to be reminded.
    
    Returns
    ----------
    True if any.
    """
    from db import DB
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
    try:
        from db import DB
        db = DB()
        db.open()
        params = (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),)
        ret = db.execute('SELECT id, user_id, name, important, stop FROM %d.todo_task WHERE completed = FALSE AND remind IS NOT NULL AND remind < ? ORDER BY remind', params)
        for x in ret:
            task = {}
            task['id'] = x[0]
            task['user_id'] = x[1]
            task['name'] = x[2]
            task['important'] = x[3]
            if (len(str(x[4])) == 19):
                task['stop'] = datetime.strptime(str(x[4]), '%Y-%m-%d %H:%M:%S')
            else:
                task['stop'] = datetime.strptime(str(x[4]), '%Y-%m-%d %H:%M:%S.%f')
            remind_one_task(log, db, task)
    
        db.close()
    except:
        log('[x] process() [service/todo.py] Exception: ' + str(sys.exc_info()[0]))

def remind_one_task(log, db, task):
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_cert)
        firebase_admin.initialize_app(cred)

    body = 'Termin: ' + task['stop'].strftime('%a, %d %b %Y %H:%M')
    n = messaging.Notification(title = task['name'], body = body, image = None)
    if (task['important'] != 0):
        priority = 'high'
    else:
        priority = 'normal'
    myicon = 'https://rusel.by/static/rusel.png'
    mybadge = ''
    click_action = 'https://rusel.by/todo/' + str(task['id']) + '/'
    an = messaging.AndroidNotification(title=task['name'], body=body, icon=myicon, color=None, sound=None, tag=None, click_action=click_action, body_loc_key=None, \
                                       body_loc_args=None, title_loc_key=None, title_loc_args=None, channel_id=None, image=None, ticker=None, sticky=None, \
                                       event_timestamp=None, local_only=None, priority=None, vibrate_timings_millis=None, default_vibrate_timings=None, \
                                       default_sound=None, light_settings=None, default_light_settings=None, visibility=None, notification_count=None)
    messaging.AndroidConfig(collapse_key=None, priority=priority, ttl=None, restricted_package_name=None, data=None, notification=an, fcm_options=None)
    actions = []
    a1 = messaging.WebpushNotificationAction('postpone', 'Postpone 1 hour', icon='https://rusel.by/static/icons/postpone.png')
    a2 = messaging.WebpushNotificationAction('done', 'Done', icon='https://rusel.by/static/icons/completed.png')
    actions.append(a1)
    actions.append(a2)

    wn = messaging.WebpushNotification(title=task['name'], body=body, icon=myicon, badge=mybadge, actions=actions, tag=str(task['id']), custom_data={"click_action": click_action})
    messaging.WebpushFCMOptions(click_action)
    wc = messaging.WebpushConfig(headers=None, data=None, notification=wn, fcm_options=None)
    
    ret = db.execute('SELECT token FROM %d.todo_subscription WHERE user_id = ?', (task['user_id'],))
    tokens = []
    for x in ret:
        tokens.append(x[0])
    
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
            db.execute('DELETE FROM %d.todo_subscription WHERE token = ?', (tokens[npp-1],))
            log('Token deleted')
        npp += 1

    db.execute('UPDATE %d.todo_task SET last_remind = ?, remind = NULL WHERE id = ?', (datetime.now(), task['id']))

