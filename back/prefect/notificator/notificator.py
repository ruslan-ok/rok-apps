import firebase_admin
import psycopg2
from datetime import datetime, date
from prefect import flow, task
from firebase_admin import credentials, messaging
from notificator_params import HOST, PORT, DB, USER, PWD, FIREBASE_ACCOUNT_CERT, DJANGO_HOST_API

READY_TASKS_SQL = """
SELECT
	t.id as task_id,
	case when g5.id is null then '' else g5.name || '/' end ||
	case when g4.id is null then '' else g4.name || '/' end ||
	case when g3.id is null then '' else g3.name || '/' end ||
	case when g2.id is null then '' else g2.name || '/' end ||
	case when g1.id is null then '' else g1.name end as group_path,
	t.name,
	t.user_id,
	t.important,
	t.stop,
	t.remind
FROM task_task t
LEFT JOIN task_taskgroup tg
	ON t.id = tg.task_id
	AND tg.role = 'todo'
LEFT JOIN task_group g1
	ON tg.group_id = g1.id
LEFT JOIN task_group g2
	ON g1.node_id = g2.id
LEFT JOIN task_group g3
	ON g2.node_id = g3.id
LEFT JOIN task_group g4
	ON g3.node_id = g4.id
LEFT JOIN task_group g5
	ON g4.node_id = g5.id
WHERE 1=1
	AND t.completed = false
	AND t.remind is not NULL
	AND t.remind < NOW();
"""

TOKENS_SQL = """
SELECT user_id, token
FROM todo_subscription
WHERE user_id in %(user_ids)s;
"""

DELETE_TOKEN_SQL = """
DELETE FROM todo_subscription
WHERE user_id = %(user_id)s
	AND token = %(token)s;
"""

RESET_TASK_SQL = """
UPDATE task_task
SET
	first_remind = CASE WHEN first_remind is NULL THEN remind ELSE first_remind END,
	remind = NULL,
	last_remind = NOW()
WHERE id = %(task_id)s;
"""

def b_expired(stop: datetime):
    return (stop < datetime.now()) and ((stop.date() != date.today()) or (stop.hour != 0) or (stop.minute != 0))

def s_termin(stop: datetime):
    if b_expired(stop):
        s = 'Expired, '
    else:
        s = 'Termin: '
    return s + stop.strftime('%d.%m.%Y')

@task(log_prints=True, task_run_name='{name}', tags=['reminder'])
def remind_one_task(name: str, row, tokens: list[str], cur):
    task_id = row[0]
    group_path = row[1]
    task_name = row[2]
    user_id = row[3]
    task_important = row[4]
    task_stop = row[5].replace(tzinfo=None)

    if not tokens:
        print('No tokens for user_id = ' + str(user_id))
        return
    
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_ACCOUNT_CERT)
        firebase_admin.initialize_app(cred)

    body = s_termin(task_stop) + ' - ' + group_path
    n = messaging.Notification(title=task_name, body=body, image=None)
    if (task_important):
        priority = 'high'
    else:
        priority = 'normal'
    myicon = DJANGO_HOST_API + '/static/rok.png'
    mybadge = ''
    click_action = DJANGO_HOST_API + '/todo/' + str(task_id) + '/'
    an = messaging.AndroidNotification(title=task_name, body=body, icon=myicon, color=None, sound=None, tag=None, click_action=click_action, body_loc_key=None, \
                                    body_loc_args=None, title_loc_key=None, title_loc_args=None, channel_id=None, image=None, ticker=None, sticky=None, \
                                    event_timestamp=None, local_only=None, priority=None, vibrate_timings_millis=None, default_vibrate_timings=None, \
                                    default_sound=None, light_settings=None, default_light_settings=None, visibility=None, notification_count=None)
    messaging.AndroidConfig(collapse_key=None, priority=priority, ttl=None, restricted_package_name=None, data=None, notification=an, fcm_options=None)
    actions = []
    a1 = messaging.WebpushNotificationAction('postpone', 'Postpone 1 hour', icon=DJANGO_HOST_API+'/static/todo/icons/postpone.png')
    a2 = messaging.WebpushNotificationAction('done', 'Done', icon=DJANGO_HOST_API+'/static/todo/icons/completed.png')
    actions.append(a1)
    actions.append(a2)

    wn = messaging.WebpushNotification(title=task_name, body=body, icon=myicon, badge=mybadge, actions=actions, tag=str(task_id), custom_data={"click_action": click_action})
    messaging.WebpushFCMOptions(click_action)
    wc = messaging.WebpushConfig(headers=None, data=None, notification=wn, fcm_options=None)

    mm = messaging.MulticastMessage(tokens=tokens, data=None, notification=n, android=None, webpush=wc, apns=None, fcm_options=None)
    r = messaging.send_each_for_multicast(mm, dry_run=False, app=None)
    ret_resp = '[' + str(len(r.responses)) + ']'
    if r.failure_count:
        prefix = 'WARNING'
    else:
        prefix = 'INFO'
    print(f'[{prefix}] Remind task ID: {task_id}, ok: {r.success_count}, err: {r.failure_count}, resp: {ret_resp}, name: "{task_name}"')
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
        print('[DEBUG] Remind status {}. {}{}{}\n       token "{}"'.format(npp, status, error_desc, msg, tokens[npp-1]))
        if (not z.success) and (z.exception.code == 'NOT_FOUND'):
            cur.execute(DELETE_TOKEN_SQL, {'user_id': user_id, 'token': tokens[npp-1]})
            print('[ERROR] Token deleted')
        npp += 1

    cur.execute(RESET_TASK_SQL, {'task_id': task_id})

@flow(log_prints=True)
def check_notificator():
    try:
        with  psycopg2.connect(host=HOST, port=PORT, database=DB, user=USER, password=PWD) as conn:
            with  conn.cursor() as cur:
                cur.execute(READY_TASKS_SQL)
                rows = cur.fetchall()
                qnt = len(rows)
                print(f'Tasks to notify: {qnt}')

                if qnt:
                    user_ids = [row[3] for row in rows]
                    user_ids = tuple(list(set(user_ids)))
                    cur.execute(TOKENS_SQL, {'user_ids': user_ids})
                    tokens = cur.fetchall()

                    for row in rows:
                        user_tokens = [token[1] for token in tokens if token[0] == row[3]]
                        remind_one_task(f'Reminder for task {row[2]}', row, user_tokens, cur)
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)    


if __name__ == '__main__':
    check_notificator()
