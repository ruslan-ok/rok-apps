import firebase_admin
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError

from django.conf import settings

def test_firebase_call():
    print('1')
    if not firebase_admin._apps:
        cred_cert = settings.FIREBASE_ACCOUNT_CERT
        cred = credentials.Certificate(cred_cert)
        default_app = firebase_admin.initialize_app(cred)

    print('2')
    body = 'Remind time 00:00'
    n = messaging.Notification(title = 'test_firebase_call', body = body, image = None)
    priority = 'normal'
    myicon = 'https://rok-apps.com/static/rok/img/test-192.png'
    mybadge = 'https://rok-apps.com/static/rok/img/test-72.png'
    click_action = 'https://rok-apps.com/todo/99999/'
    an = messaging.AndroidNotification(title = 'test_firebase_call', body = body, icon = myicon, color = None, sound = None, tag = None, click_action = click_action, body_loc_key = None, \
                                       body_loc_args = None, title_loc_key = None, title_loc_args = None, channel_id = None, image = None, ticker = None, sticky = None, \
                                       event_timestamp = None, local_only = None, priority = None, vibrate_timings_millis = None, default_vibrate_timings = None, \
                                       default_sound = None, light_settings = None, default_light_settings = None, visibility = None, notification_count = None)
    añ = messaging.AndroidConfig(collapse_key = None, priority = priority, ttl = None, restricted_package_name = None, data = None, notification = an, fcm_options = None)
    actions = []
    a1 = messaging.WebpushNotificationAction('postpone', 'Postpone', icon = 'https://rok-apps.com/static/todo/icon/remind-today.png')
    a2 = messaging.WebpushNotificationAction('done', 'Done', icon = 'https://rok-apps.com/static/rok/icon/delete.png')
    actions.append(a1)
    actions.append(a2)

    print('3')
    #wn = messaging.WebpushNotification(title = task.name, body = body, icon = icon, actions = actions, badge = None, data = None, direction = None, image = None, language = None, renotify = True, require_interaction = True, silent = False, tag = None, timestamp_millis = None, vibrate = None, custom_data = None)
    wn = messaging.WebpushNotification(title = 'test_firebase_call', body = body, icon = myicon, badge = mybadge, actions = actions, tag = '99999', custom_data = {"click_action": click_action})
    wo = messaging.WebpushFCMOptions(click_action)
    wc = messaging.WebpushConfig(headers = None, data = None, notification = wn, fcm_options = None)
    
    tokens = []
    tokens.append('dq6oUJNrQ2IYcm3mVtzfw8:APA91bE_3q9CdIAMWw6Blh0uGmLve5dv_AeHY4kJec6tGM34Vw3wMN6WIEZveI60Yl0neNeeSzmD1zwcvuC0A49Ht7t90mHxD47jE8duyQX0090qRflS7hVo0lm-qJ_wLJsJ59_nJFtQ')
    
    print('4')
    mm = messaging.MulticastMessage(tokens = tokens, data = None, notification = n, android = None, webpush = wc, apns = None, fcm_options = None)
    print('5')
    r = messaging.send_multicast(mm, dry_run = False, app = None)
    print('6')
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
    
if __name__ == '__main__':
    test_firebase_call()
