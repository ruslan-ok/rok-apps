from datetime import datetime, timedelta
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from task.models import Task
from todo.models import Subscription

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def fcm(request):
    if (request.method == 'POST'):
        if ('app_token_add' in request.POST):
            subscription = Subscription.objects.create(user=request.user, token=request.POST['app_token'])
            return HttpResponseRedirect(reverse('todo:fcm'))
        if ('app_token_del' in request.POST):
            token_id = request.POST['app_token_id']
            token = get_object_or_404(Subscription.objects.filter(id=token_id))
            token.delete()
            return HttpResponseRedirect(reverse('todo:fcm'))
    context = {}
    context['object_list'] = Subscription.objects.filter(user=request.user.id)
    template_file = 'todo/fcm.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))


def fcm_add(request):
    token = request.GET['token']
    if token:
        if not Subscription.objects.filter(user=request.user.id, token=token).exists():
            subscription = Subscription.objects.create(user=request.user, token=token)
            return HttpResponse('true')
    return HttpResponse('false')


def fcm_del(request):
    token = request.GET['token']
    if token:
        if Subscription.objects.filter(user=request.user.id, token=token).exists():
            subscription = Subscription.objects.filter(user=request.user.id, token=token).get()
            subscription.delete()
            return HttpResponse('true')
    return HttpResponse('false')

def fcm_postpone(request, pk):
    task = get_object_or_404(Task.objects.filter(user=request.user.id, id=pk))
    if not task.first_remind:
        task.first_remind = task.remind
    task.remind = (datetime.now() + timedelta(hours=1))
    task.save()
    return HttpResponse('ok, id = ' + str(task.id) + ', remind time = ' + task.remind.strftime('%H:%M'))

def fcm_done(request, pk):
    task = get_object_or_404(Task.objects.filter(user=request.user.id, id=pk))
    task.toggle_completed()
    return HttpResponse('ok')


