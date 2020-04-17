from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext_lazy as _
from trip.models import trip_summary

def rok_render(request, template, title, hide_title = False): 
    context = {}
    context['site_header'] = get_current_site(request).name
    context['title'] = title
    context['hide_title'] = hide_title
    context['trip_summary'] = trip_summary(request.user.id)
    template = loader.get_template(template)
    return HttpResponse(template.render(context, request))

def index(request):
    if request.user.is_authenticated:
        title = _('applications').capitalize()
        hide_title = False
    else:
        title = get_current_site(request)
        hide_title = True
    return rok_render(request, 'index.html', title, hide_title)

def feedback(request):
    return rok_render(request, 'feedback.html', _('feedback').capitalize())


