import os
from django.http import HttpResponse
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from rusel.context import get_base_context
#from trip.models import trip_summary

from task.const import APP_HOME, ROLE_ACCOUNT
from task.models import Task, VisitedHistory
from rusel.base.views import BaseListView
from rusel.config import app_config
from rusel.context import MAX_LAST_VISITED
from rusel.app_doc import get_app_doc, get_app_thumbnail

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
            #context['trip_summary'] = trip_summary(request.user.id)
            context['weather_api_key'] = os.environ.get('OPENWEATHER_API_KEY')
            context['weather_city_id'] = os.environ.get('OPENWEATHER_CITY_ID')

            context['last_visited'] = VisitedHistory.objects.filter(user=request.user.id).order_by('-stamp')[:MAX_LAST_VISITED]

        template = loader.get_template('index_user.html')
        return HttpResponse(template.render(context, request))

def get_doc(request, role, pk, fname):
    return get_app_doc(request, role, pk, fname)

def get_thumbnail(request, role, pk, fname):
    return get_app_thumbnail(request, role, pk, fname)

