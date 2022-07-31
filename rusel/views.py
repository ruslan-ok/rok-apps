import os, datetime, django, rest_framework, OpenSSL, ssl, urllib.request
from platform import python_version
from django.http import HttpResponse
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from rusel.context import get_base_context
#from trip.models import trip_summary
from logs.site_stat import get_site_stat
from .mysql_ver import get_mysql_ver

from task.const import APP_HOME, ROLE_ACCOUNT
from task.models import Task, VisitedHistory
from rusel.base.views import BaseListView
from rusel.config import app_config
from rusel.context import MAX_LAST_VISITED
from rusel.app_doc import get_app_doc, get_app_thumbnail
from task.models import ServiceEvent

class TuneData:
    def tune_dataset(self, data, group):
        return data

class ListView(BaseListView, TuneData):
    model = Task
    fields = {'name'}

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, ROLE_ACCOUNT, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            context = get_base_context(request, APP_HOME, ROLE_ACCOUNT, None, '', ('rusel.by',))
            template = loader.get_template('index_anonim.html')
            return HttpResponse(template.render(context, request))

        query = None
        if (self.request.method == 'GET'):
            query = self.request.GET.get('q')
        if query:
            super().get(request, *args, **kwargs)
            context = self.get_context_data(**kwargs)
            template = loader.get_template('base/list.html')
            return HttpResponse(template.render(context, request))

        context = get_base_context(request, APP_HOME, ROLE_ACCOUNT, None, '', (_('applications').capitalize(),))
        context['debug'] = settings.DEBUG
        config = {'app_title': 'rusel.by'}
        context['config'] = config

        if (request.user.username == 'ruslan.ok'):
            statistics = get_site_stat(request.user)
            indicators = statistics[0]
            stat = statistics[1]
            context['indicators'] = indicators
            context['show_stat'] = (len(stat) > 0)
            context['stat'] = stat
            #context['trip_summary'] = trip_summary(request.user.id)
            context['python_version'] = python_version()
            context['django_version'] = '{}.{}.{} {}'.format(*django.VERSION)
            context['drf_version'] = '{}'.format(rest_framework.VERSION)
            context['weather_api_key'] = os.environ.get('OPENWEATHER_API_KEY')
            context['weather_city_id'] = os.environ.get('OPENWEATHER_CITY_ID')
            host = os.environ.get('DJANGO_HOST')
            api_host = os.environ.get('DJANGO_HOST_API')
            if host != 'localhost':
                response = urllib.request.urlopen(api_host)
                versions = response.headers['Server'].split(' ')
                for ver in versions:
                    if 'Apache' in ver:
                        context['apache_version'] = ver.split('/')[1]
                    if 'OpenSSL' in ver:
                        context['openssl_version'] = ver.split('/')[1]
                    if 'mod_wsgi' in ver:
                        context['mod_wsgi_version'] = ver.split('/')[1]
            context['hmail_version'] = '5.6.7 bld 2425'
            context['mysql_version'] = get_mysql_ver()
            context['leaflet_version'] = get_leaflet_ver()
            context['bootstrap_version'] = get_bootstrap_ver()
            context['izitoast_version'] = get_izitoast_ver()
            context['chartjs_version'] = get_chartjs_ver()
            context['swiper_version'] = get_swiper_ver()
            context['firebase_version'] = get_firebase_ver()

            try:
                cert = ssl.get_server_certificate(('rusel.by', 443))
                x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
                t = x509.get_notAfter()
                d = datetime.date(int(t[0:4]),int(t[4:6]),int(t[6:8]))
                context['cert_termin'] = d.strftime('%d.%m.%Y')
            except:
                pass

            context['last_visited'] = VisitedHistory.objects.filter(user=request.user.id).order_by('-stamp')[:MAX_LAST_VISITED]
            context['event_log'] = ServiceEvent.objects.all().exclude(app='service', service='manager', type='info', name='call').order_by('-created')[:25]

            bss_status = 'stoped'
            last_start = None
            last_call = None
            start_events = ServiceEvent.objects.filter(app='service', service='manager', type='info', name='start').order_by('-created')
            call_events = ServiceEvent.objects.filter(app='service', service='manager', type='info', name='call').order_by('-created')
            if len(call_events) > 0:
                last_call = call_events[0].created
            if len(start_events) > 0:
                last_start = start_events[0].created
                if not last_call or last_call < last_start:
                    last_call = last_start
            if last_call:
                sec = (datetime.datetime.now() - last_call).total_seconds()
                if sec < 120:
                    bss_status = 'work'
            context['bss'] = bss_status

        template = loader.get_template('index_user.html')
        return HttpResponse(template.render(context, request))


def get_leaflet_ver():
    return '1.7.1'

def get_bootstrap_ver():
    return '5.1.0'

def get_izitoast_ver():
    return '1.4.0'

def get_chartjs_ver():
    return '3.7.0'

def get_swiper_ver():
    return '8.0.7'

def get_firebase_ver():
    return '5.2.0'


def get_doc(request, role, pk, fname):
    return get_app_doc(request, role, pk, fname)

def get_thumbnail(request, role, pk, fname):
    return get_app_thumbnail(request, role, pk, fname)

