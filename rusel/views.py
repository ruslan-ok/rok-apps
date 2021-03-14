import datetime
import django
import OpenSSL
import ssl, socket
from platform import python_version
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.views import View

from hier.utils import get_base_context_ext, process_common_commands, get_param
from hier.models import Param, Folder
from trip.models import trip_summary
from hier.log_parser import start_log_parser
from hier.params import get_search_info

from note.search import search as note_search
from todo.search import search as todo_search
from proj.search import search as proj_search
from trip.search import search as trip_search
from fuel.search import search as fuel_search
from wage.search import search as wage_search
from apart.search import search as apart_search
from store.search import search as store_search

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
    template = loader.get_template('index_anonim.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def index_user(request):
    process_common_commands(request, app_name)
    app_param, context = get_base_context_ext(request, app_name, '', _('applications').capitalize())
    context['hide_title'] = False
    context['aside_disabled'] = True

    query = None
    data = []
    if (request.method == 'GET'):
        query = request.GET.get('q')
        context['search_info'] = get_search_info(query)
        data = get_search_data(request.user, app_param, query)
        context['search_qty'] = len(data)
        context['search_data'] = data
        if query:
            context['title'] = _('search results').capitalize()
    if not data:
        if (request.user.username == 'ruslan.ok'):
            try:
                context['logs'] = start_log_parser()
            except Exception as inst:
                context['logs'] = ((('type', str(type(inst))),
                                    ('args', inst.args),
                                    ('inst', inst),
                                    ),)
            context['trip_summary'] = trip_summary(request.user.id)
            context['python_version'] = python_version()
            context['django_version'] = '{}.{}.{} {}'.format(*django.VERSION)
            context['apache_version'] = '2.4.41 (Win64)'
            context['hmail_version'] = '5.6.7 - Build 2425'
        
            #cursor = connection.cursor()
            #cursor.execute('SHOW VARIABLES LIKE "version"')
            #context['mysql_version'] = cursor.fetchone()
            context['mysql_version'] = '8.0.19'
        
            cert = ssl.get_server_certificate(('rusel.by', 443))
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
            t = x509.get_notAfter()
            d = datetime.date(int(t[0:4]),int(t[4:6]),int(t[6:8]))
            context['cert_termin'] = d.strftime('%d.%m.%Y')

        param = get_param(request.user)
        if param and param.last_url:
            try:
                context['last_visited_url'] = reverse(param.last_url)
            except NoReverseMatch:
                pass
            context['last_visited_app'] = param.last_app
            context['last_visited_page'] = param.last_page

    if query:
        template = loader.get_template('index_search.html')
    else:
        template = loader.get_template('index_user.html')
    return HttpResponse(template.render(context, request))

def get_si_date(e):
    if not e.created:
        return datetime.datetime(2000,1,1).date()
    return e.created

def get_search_data(user, app_param, query):
    if not query:
        return []
    data = []
    data += note_search(user, query)
    data += todo_search(user, query)
    data += proj_search(user, query)
    data += trip_search(user, query)
    data += fuel_search(user, query)
    data += wage_search(user, query)
    data += apart_search(user, query)
    data += store_search(user, query)
    data.sort(reverse=True, key=get_si_date)
    return data


#----------------------------------
# Feedback
#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def feedback(request):
    context = get_base_context(request, 0, 0, _('feedback'))
    template = loader.get_template('feedback.html')
    return HttpResponse(template.render(context, request))


