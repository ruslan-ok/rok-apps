import os, json, requests
from decimal import Decimal
from datetime import datetime
from django.http import Http404
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from core.views import Context
from core.hp_widget.delta import get_start_date, approximate, ChartPeriod, ChartDataVersion, SourceData
from health.config import app_config
from health.forms.temp_filter import TempFilter
from task.const import NUM_ROLE_MARKER, ROLE_CHART_WEIGHT, ROLE_CHART_WAIST, ROLE_CHART_TEMP
from task.models import Task

class WeightView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView, Context):
    template_name = "health/chart.html"
    permission_required = 'task.view_health'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(app_config, ROLE_CHART_WEIGHT)

    def get_context_data(self, **kwargs):
        if not self.request.user.is_authenticated:
            raise Http404
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context(self.request.user.id, None, icon=self.config.role_icon, nav_items=self.get_nav_items()))
        context['title'] = _('Weight chart')
        context['mark'] = 'weight'
        context['hide_add_item_input'] = True
        return context

class WaistView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView, Context):
    template_name = "health/chart.html"
    permission_required = 'task.view_health'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(app_config, ROLE_CHART_WAIST)

    def get_context_data(self, **kwargs):
        if not self.request.user.is_authenticated:
            raise Http404
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context(self.request.user.id, None, icon=self.config.role_icon, nav_items=self.get_nav_items()))
        context['title'] = _('Waist chart')
        context['mark'] = 'waist'
        context['hide_add_item_input'] = True
        return context

class TempView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView, Context):
    template_name = "health/chart.html"
    permission_required = 'task.view_health'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(app_config, ROLE_CHART_TEMP)

    def get_context_data(self, **kwargs):
        if not self.request.user.is_authenticated:
            raise Http404
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context(self.request.user.id, None, icon=self.config.role_icon, nav_items=self.get_nav_items()))
        context['title'] = _('Temperature chart')
        context['mark'] = 'temp'
        context['hide_add_item_input'] = True
        context['form'] = TempFilter()
        return context

#----------------------------------
def get_data_from_db(user_id: int, name, period: ChartPeriod) -> list:
    src_data: list[SourceData] = []
    chart_data = []

    match name:
        case 'weight': 
            data = Task.objects.filter(user=user_id, app_health=NUM_ROLE_MARKER).exclude(bio_weight=None).exclude(bio_weight=0)
            enddate: datetime = datetime.today()
            if data.exists():
                last_rec = data.order_by('-event')[0]
                if last_rec and last_rec.event:
                    enddate = last_rec.event
            startdate = get_start_date(enddate, period)
            data = data.filter(event__gt=startdate).order_by('event')
            src_data = [SourceData(event=x.event, value=x.bio_weight) for x in data if x.event and x.bio_weight]
        case 'waist': 
            data = Task.objects.filter(user=user_id, app_health=NUM_ROLE_MARKER).exclude(bio_waist=None).exclude(bio_waist=0).order_by('event')
            src_data = [SourceData(event=x.event, value=Decimal(x.bio_waist)) for x in data if x.event and x.bio_waist]

    chart_data = approximate(period, src_data, 200)
    return chart_data

#----------------------------------
def build_weight_chart(user_id: int, period: ChartPeriod, version: ChartDataVersion):
    values = get_data_from_db(user_id, 'weight', period)
    if version == ChartDataVersion.v2:
        current = change = None
        if values:
            current = values[-1].y
            change = values[-1].y - values[0].y
        data = {
            'data': values,
            'current': current,
            'change': change,
        }
    else:
        data = {
            'type': 'line',
            'data': {'labels': [item['x'] for item in values],
                'datasets': [{
                    'label': 'Weight, kg',
                    'data': [item['y'] for item in values],
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1,
                    'tension': 0.4,
                }]
            },
        }
    return data

def get_api_health_chart(period: ChartPeriod, version: ChartDataVersion):
    api_url = os.environ.get('DJANGO_HOST_LOG', '')
    service_token = os.environ.get('DJANGO_SERVICE_TOKEN', '')
    headers = {'Authorization': 'Token ' + service_token, 'User-Agent': 'Mozilla/5.0'}
    verify = os.environ.get('DJANGO_CERT', '')
    resp = requests.get(api_url + '/api/get_chart_data/?mark=health&version=' + version.value + '&period=' + period.value, headers=headers, verify=verify)
    if (resp.status_code != 200):
        return None
    return json.loads(resp.content)

def build_health_chart(user_id: int, period: ChartPeriod, version: ChartDataVersion):
    if os.environ.get('DJANGO_DEVICE', 'Nuc') != os.environ.get('DJANGO_LOG_DEVICE', 'Nuc'):
        ret = get_api_health_chart(period, version)
        if ret:
            return ret
    values = get_data_from_db(user_id, 'weight', period)

    if version == ChartDataVersion.v2:
        current = change = None
        if values:
            current = values[-1]['y']
            change = values[-1]['y'] - values[0]['y']
        data = {
            'data': values,
            'current': current,
            'change': change,
        }
    else:
        data = {
            'type': 'line',
            'data': {'labels': [item['x'] for item in values],
                'datasets': [{
                    'label': 'Weight, kg',
                    'data': [item['y'] for item in values],
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                    'borderColor': 'rgba(255, 99, 132, 1)',
                    'borderWidth': 1,
                    'tension': 0.4,
                }]
            },
            'options': {
                'plugins': {
                    'legend': {
                        'display': False,
                    },
                },
                'elements': {
                    'point': {
                        'radius': 0,
                    },
                },
            },
        }
    return data

def build_waist_chart(user_id: int):
    values = get_data_from_db(user_id, 'waist', ChartPeriod.p10y)

    data = {
        'type': 'line',
        'data': {'labels': [item['x'] for item in values],
            'datasets': [{
                'label': 'Waist, cm',
                'data': [item['y'] for item in values],
                'backgroundColor': 'rgba(111, 184, 71, 0.2)',
                'borderColor': 'rgba(111, 184, 71, 1)',
                'borderWidth': 1,
                'tension': 0.4,
            }]
        },
    }
    return data

def build_temp_chart(user_id: int, filter):
    x = []
    y = []
    values = Task.objects.filter(user=user_id, app_health=NUM_ROLE_MARKER).exclude(bio_temp=None).exclude(bio_temp=0).order_by('event')
    if filter:
        filter_id = int(filter)
        if filter_id:
            incident = Task.objects.filter(id=filter_id).get()
            if incident.start:
                values = values.filter(event__gte=incident.start)
            if incident.stop:
                values = values.filter(event__lte=incident.stop)
    for t in values:
        if t.event:
            x.append(t.event.strftime('%Y-%m-%d %H:%M'))
            y.append(t.bio_temp)

    data = {
        'type': 'line',
        'data': {'labels': x,
            'datasets': [{
                'label': 'Temperature, °C',
                'data': y,
                'backgroundColor': 'rgba(111, 99, 255, 0.2)',
                'borderColor': 'rgba(111, 99, 255, 1)',
                'borderWidth': 1,
                'tension': 0.4,
            }]
        },
        'options': {
            'scales': {
                'xAxis': {
                    'type': 'time',
                    'display': True,
                }
            }
        }
    }
    return data

def get_chart_data(user_id: int, mark: str, period: ChartPeriod, version: ChartDataVersion, filter=None):
    data = {}
    match mark:
        case 'weight': data = build_weight_chart(user_id, period, version)
        case 'waist': data = build_waist_chart(user_id)
        case 'temp': data = build_temp_chart(user_id, filter)
        case 'health': data = build_health_chart(user_id, period, version)
    return data