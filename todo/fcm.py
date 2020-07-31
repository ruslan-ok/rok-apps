import sys
import requests
from datetime import datetime, timedelta

from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import firebase_admin
from firebase_admin import credentials, messaging
from firebase_admin.exceptions import FirebaseError

from .models import Task, Subscription
from .secret import url, cacert, cred_cert, log_path

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def fcm(request):
    if (request.method == 'POST'):
        if ('app_token_add' in request.POST):
            subscription = Subscription.objects.create(user = request.user, token = request.POST['app_token'])
            return HttpResponseRedirect(reverse('todo:fcm'))
        if ('app_token_del' in request.POST):
            token_id = request.POST['app_token_id']
            token = get_object_or_404(Subscription.objects.filter(id = token_id))
            token.delete()
            return HttpResponseRedirect(reverse('todo:fcm'))
    context = {}
    context['object_list'] = Subscription.objects.filter(user = request.user.id)
    template_file = 'todo/fcm.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))


def fcm_add(request):
    token = request.GET['token']
    if token:
        if not Subscription.objects.filter(user = request.user.id, token = token).exists():
            subscription = Subscription.objects.create(user = request.user, token = token)
            return HttpResponse('true')
    return HttpResponse('false')


def fcm_del(request):
    token = request.GET['token']
    if token:
        if Subscription.objects.filter(user = request.user.id, token = token).exists():
            subscription = Subscription.objects.filter(user = request.user.id, token = token).get()
            subscription.delete()
            return HttpResponse('true')
    return HttpResponse('false')


def remind_one_task(task, debug = False):
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_cert)
        default_app = firebase_admin.initialize_app(cred)

    if debug:
        rt = datetime.now()
    else:
        rt = task.remind_time
    body = '{} {}'.format(_('remind time').capitalize(), rt.strftime('%H:%M'))
    #if task.info:
    #    body += '\n' + task.info
    n = messaging.Notification(title = task.name, body = body, image = None)
    if task.important:
        priority = 'high'
    else:
        priority = 'normal'
    icon = 'https://rusel.by/favicon.ico'
    click_action = 'https://rusel.by/todo/task/' + str(task.id) + '/'
    an = messaging.AndroidNotification(title = task.name, body = body, icon = icon, color = None, sound = None, tag = None, click_action = click_action, body_loc_key = None, \
                                       body_loc_args = None, title_loc_key = None, title_loc_args = None, channel_id = None, image = None, ticker = None, sticky = None, \
                                       event_timestamp = None, local_only = None, priority = None, vibrate_timings_millis = None, default_vibrate_timings = None, \
                                       default_sound = None, light_settings = None, default_light_settings = None, visibility = None, notification_count = None)
    aс = messaging.AndroidConfig(collapse_key = None, priority = priority, ttl = None, restricted_package_name = None, data = None, notification = an, fcm_options = None)
    actions = []
    a1 = messaging.WebpushNotificationAction('delay', _('delay').capitalize(), icon = 'https://rusel.by/static/todo/icon/remind-today.png')
    a2 = messaging.WebpushNotificationAction('ready', _('ready').capitalize(), icon = 'https://rusel.by/static/rok/icon/delete.png')
    actions.append(a1)
    actions.append(a2)

    #wn = messaging.WebpushNotification(title = task.name, body = body, icon = icon, actions = actions, badge = None, data = None, direction = None, image = None, language = None, renotify = True, require_interaction = True, silent = False, tag = None, timestamp_millis = None, vibrate = None, custom_data = None)
    wn = messaging.WebpushNotification(title = task.name, body = body, actions = actions, tag = str(task.id), custom_data = {"click_action": click_action})
    wo = messaging.WebpushFCMOptions(click_action)
    wc = messaging.WebpushConfig(headers = None, data = None, notification = wn, fcm_options = None)
    
    tokens = []
    for s in Subscription.objects.filter(user = task.user.id):
        tokens.append(s.token)
    
    mm = messaging.MulticastMessage(tokens = tokens, data = None, notification = n, android = None, webpush = wc, apns = None, fcm_options = None)
    r = messaging.send_multicast(mm, dry_run = False, app = None)
    ret_resp = '[' + str(len(r.responses)) + ']: '
    for z in r.responses:
        if (len(ret_resp) > 0):
            ret_resp += ', '
        if z.success:
            ret_resp += '1'
        else:
            ret_resp += '0'
        if z.message_id:
            ret_resp += ':' + z.message_id
    
    ret = 'ok: ' + str(r.success_count) + ', err: ' + str(r.failure_count) + ', resp: ' + ret_resp
    task.reminder = False
    task.save()

    return ret


def fcm_send(request, pk):
    task = get_object_or_404(Task.objects.filter(id = pk, user = request.user.id))
    status = remind_one_task(task)
    #return HttpResponse('fcm_send: ' + status)
    return HttpResponseRedirect(reverse('todo:task_list'))


def fcm_check(request):
    ret = 'ok'
    try:
        tasks = Task.objects.filter(reminder = True).order_by('remind_time')
        now = datetime.now()
        for task in tasks:
            if (task.remind_time <= now):
                rot = remind_one_task(task)
                ret += ' * "' + task.name + '" ' + rot
    except:
        ret = str(sys.exc_info()[0])

    return HttpResponse(ret)


def log(info):
    with open(log_path + 'test.log', 'a') as f:
         f.write(datetime.now().strftime('%H:%M:%S') + '   ' + info + '\n')


def fcm_delay(request, pk):
    log('fcm_delay(..., pk = ' + str(pk) + ')')
    task = get_object_or_404(Task.objects.filter(id = pk))
    task.remind_time = (datetime.now() + timedelta(seconds = 300))
    task.reminder = True
    task.save()
    log('saved: id = ' + str(task.id) + ', remind = ' + str(task.reminder) + ', time = ' + task.remind_time.strftime('%H:%M'))
    return HttpResponse('ok, id = ' + str(task.id) + ', remind = ' + str(task.reminder) + ', time = ' + task.remind_time.strftime('%H:%M'))


def fcm_ready(request, pk):
    log('fcm_ready(..., pk = ' + str(pk) + ')')
    task = get_object_or_404(Task.objects.filter(id = pk))
    task.reminder = False
    task.completed = True
    task.completion = datetime.now()
    task.save()
    log('saved: id = ' + str(task.id) + ', remind = ' + str(task.reminder) + ', time = ' + task.remind_time.strftime('%H:%M'))
    return HttpResponse('ok')


def fcm_test2(request):
    task = Task.objects.filter(name = 'Напоминания - исполнение').get()
    ret = 'ok'
    remind_one_task(task, True)
    return HttpResponse(ret + ' * "' + task.name + '" ')


def fcm_test(request):
    response = requests.get(url, verify = cacert)
    return HttpResponse(response.content.decode('utf-8'))


