import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, messaging
from logs.models import EventType
from task.models import Task, TaskGroup
from todo.models import Subscription
from task.const import ROLE_TODO
from service.site_service import SiteService
from logs.logger import Logger


logger = Logger(__name__)


class Notificator(SiteService):

    def __init__(self, *args, **kwargs):
        super().__init__('Рассылка уведомлений о задачах', *args, **kwargs)
        self.host = os.environ.get('DJANGO_HOST_API', 'http://localhost:8000')
        self.cred_cert = os.environ.get('FIREBASE_ACCOUNT_CERT')

    def ripe(self):
        """Are there any tasks that need to be reminded.
        
        Returns
        ----------
        True if any.
        """
        if 'localhost' in self.host:
            return False, False
        now = datetime.now()
        self.tasks = Task.objects.filter(completed=False, remind__lt=now).exclude(remind=None)
        logger.info({'one_per_day': True, 'message': 'result = ' + str(len(self.tasks) > 0)})
        return len(self.tasks) > 0, False

    def process(self):
        """Generating of reminder messages.
        """
        logger.info('task qnt = ' + str(len(self.tasks)))
        ret, compl = self.ripe()
        if not ret:
            return ret
        for task in self.tasks:
            group_path = ''
            group = None
            if TaskGroup.objects.filter(task=task.id, role=ROLE_TODO).exists():
                group = TaskGroup.objects.filter(task=task.id, role=ROLE_TODO).get().group
            while group:
                if group_path:
                    group_path = '/' + group_path
                group_path = group.name + group_path
                group = group.node
            self.remind_one_task(task)
            ret = True
        return ret

    def get_tokens(self, user_id):
        subs = Subscription.objects.filter(user_id=user_id)
        tokens = []
        for s in subs:
            tokens.append(s.token)
        return tokens

    def del_token(self, user_id, token):
        ret = Subscription.objects.filter(user_id=user_id, token=token).delete()
        return len(ret) > 0

    def remind_one_task(self, task):
        logger.debug('task = ' + task.name)
        if not firebase_admin._apps:
            cred = credentials.Certificate(self.cred_cert)
            firebase_admin.initialize_app(cred)

        group_path = ''
        group = None
        if TaskGroup.objects.filter(task=task.id, role=ROLE_TODO).exists():
            group = TaskGroup.objects.filter(task=task.id, role=ROLE_TODO).get().group
        while group:
            if group_path:
                group_path = '/' + group_path
            group_path = group.name + group_path
            group = group.node

        body = task.s_termin() + ' - ' + group_path
        n = messaging.Notification(title=task.name, body=body, image=None)
        if (task.important):
            priority = 'high'
        else:
            priority = 'normal'
        myicon = self.host + '/static/rusel.png'
        mybadge = ''
        click_action = self.host + '/todo/' + str(task.id) + '/'
        an = messaging.AndroidNotification(title=task.name, body=body, icon=myicon, color=None, sound=None, tag=None, click_action=click_action, body_loc_key=None, \
                                        body_loc_args=None, title_loc_key=None, title_loc_args=None, channel_id=None, image=None, ticker=None, sticky=None, \
                                        event_timestamp=None, local_only=None, priority=None, vibrate_timings_millis=None, default_vibrate_timings=None, \
                                        default_sound=None, light_settings=None, default_light_settings=None, visibility=None, notification_count=None)
        messaging.AndroidConfig(collapse_key=None, priority=priority, ttl=None, restricted_package_name=None, data=None, notification=an, fcm_options=None)
        actions = []
        a1 = messaging.WebpushNotificationAction('postpone', 'Postpone 1 hour', icon=self.host+'/static/icons/postpone.png')
        a2 = messaging.WebpushNotificationAction('done', 'Done', icon=self.host+'/static/icons/completed.png')
        actions.append(a1)
        actions.append(a2)

        wn = messaging.WebpushNotification(title=task.name, body=body, icon=myicon, badge=mybadge, actions=actions, tag=str(task.id), custom_data={"click_action": click_action})
        messaging.WebpushFCMOptions(click_action)
        wc = messaging.WebpushConfig(headers=None, data=None, notification=wn, fcm_options=None)

        tokens = self.get_tokens(task.user.id)
        if not len(tokens):
            logger.error('No tokens for user_id = ' + str(task.user.id))
            return
        
        mm = messaging.MulticastMessage(tokens=tokens, data=None, notification=n, android=None, webpush=wc, apns=None, fcm_options=None)
        r = messaging.send_each_for_multicast(mm, dry_run=False, app=None)
        ret_resp = '[' + str(len(r.responses)) + ']'
        if r.failure_count:
            method = logger.warning
        else:
            method = logger.info
        method(f'Remind task ID: {task.id},\n ok: {r.success_count},\n err: {r.failure_count},\n resp: {ret_resp},\n name: "{task.name}"')
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
            logger.debug('Remind status {}. {}{}{}\n       token "{}"'.format(npp, status, error_desc, msg, tokens[npp-1]))
            if (not z.success) and (z.exception.code == 'NOT_FOUND'):
                self.del_token(task.user.id, tokens[npp-1])
                logger.error('Token deleted')
            npp += 1

        if not task.first_remind:
            task.first_remind = task.remind
        task.last_remind = datetime.now()
        task.remind = None
        task.save()

