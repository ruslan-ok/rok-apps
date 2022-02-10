import datetime, django, OpenSSL, ssl, urllib.request
from platform import python_version
from django.http import HttpResponse
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from rusel.context import get_base_context
#from trip.models import trip_summary
#from rusel.site_stat import get_site_stat
from .mysql_ver import get_mysql_ver

from task.const import APP_HOME, ROLE_ACCOUNT
from task.models import Task
from hier.models import VisitedHistory
from rusel.base.views import BaseListView
from rusel.config import app_config
from rusel.context import MAX_LAST_VISITED

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
            #statistics = get_site_stat(request.user)
            #indicators = statistics[0]
            #stat = statistics[1]
            #context['indicators'] = indicators
            #context['show_stat'] = (len(stat) > 0)
            #context['stat'] = stat
            #context['trip_summary'] = trip_summary(request.user.id)
            context['python_version'] = python_version()
            context['django_version'] = '{}.{}.{} {}'.format(*django.VERSION)
            response = urllib.request.urlopen('https://rusel.by')
            versions = response.headers['Server'].split(' ')
            for ver in versions:
                if 'Apache' in ver:
                    context['apache_version'] = ver.split('/')[1]
                if 'OpenSSL' in ver:
                    context['openssl_version'] = ver.split('/')[1]
                if 'mod_wsgi' in ver:
                    context['mod_wsgi_version'] = ver.split('/')[1]
            context['hmail_version'] = '5.6.7 - Build 2425'
            context['mysql_version'] = get_mysql_ver()
        
            try:
                cert = ssl.get_server_certificate(('rusel.by', 443))
                x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
                t = x509.get_notAfter()
                d = datetime.date(int(t[0:4]),int(t[4:6]),int(t[6:8]))
                context['cert_termin'] = d.strftime('%d.%m.%Y')
            except:
                pass

            context['last_visited'] = VisitedHistory.objects.filter(user=request.user.id).order_by('-stamp')[:MAX_LAST_VISITED]

        template = loader.get_template('index_user.html')
        return HttpResponse(template.render(context, request))
