from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.views import View

from hier.utils import get_base_context_ext, process_common_commands, get_trash, get_param, get_buttons
from hier.models import Param, Folder
from trip.models import trip_summary

app_name = 'rusel'

#----------------------------------
# Index
#----------------------------------
def index(request):
    if request.user.is_authenticated:
        return index_user(request)
    return index_anonim(request)

def index_anonim(request):
    app_param, context = get_base_context_ext(request, app_name, '', '')
    context['hide_title'] = True
    context['aside_disabled'] = True
    context['buttons'] = get_buttons(request.user, 0, 'content_list', 0)
    template = loader.get_template('index_anonim.html')
    return HttpResponse(template.render(context, request))

def index_user(request):
    process_common_commands(request, app_name)
    app_param, context = get_base_context_ext(request, app_name, '', _('applications').capitalize())
    context['hide_title'] = False
    context['aside_disabled'] = True
    context['trip_summary'] = trip_summary(request.user.id)
    context['buttons'] = get_buttons(request.user, 0, 'content_list', 0)
    param = get_param(request.user)
    if param and param.last_url:
        try:
            context['last_visited_url'] = reverse(param.last_url)
        except NoReverseMatch:
            pass
        context['last_visited_app'] = param.last_app
        context['last_visited_page'] = param.last_page

    template = loader.get_template('index_user.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
# Feedback
#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def feedback(request):
    context = get_base_context(request, 0, 0, _('feedback'))
    template = loader.get_template('feedback.html')
    return HttpResponse(template.render(context, request))


#----------------------------------
# Trash
#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def trash(request):
    return HttpResponseRedirect(reverse('hier:folder_list', args = [get_trash(request.user).id]))

