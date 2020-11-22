import datetime
import django
#import OpenSSL
#import ssl, socket
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

def index_user(request):
    process_common_commands(request, app_name)
    app_param, context = get_base_context_ext(request, app_name, '', _('applications').capitalize())
    context['hide_title'] = False
    context['aside_disabled'] = True
    context['trip_summary'] = trip_summary(request.user.id)
    context['python_version'] = python_version()
    context['django_version'] = '{}.{}.{} {}'.format(*django.VERSION)
    context['apache_version'] = '2.4.41 (Win64)'

    #cursor = connection.cursor()
    #cursor.execute('SHOW VARIABLES LIKE "version"')
    #context['mysql_version'] = cursor.fetchone()
    context['mysql_version'] = '8.0.19'

    context['hmail_version'] = '5.6.7 - Build 2425'

    context['cert_termin'] = '17.12.2020'
    """
    Перестало работать после обновления python 3.8.5 -> 3.9.0

    cert = ssl.get_server_certificate(('rusel.by', 443))
    x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
    t = x509.get_notAfter()
    d = datetime.date(int(t[0:4]),int(t[4:6]),int(t[6:8]))
    context['cert_termin'] = d.strftime('%d.%m.%Y')
    """

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


