import json, requests
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from django.http import Http404
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from core.views import Context
from core.hp_widget.delta import get_start_date, approximate, ChartPeriod, SourceData, build_chart_config
from health.forms.temp_filter import TempFilter
from task.const import NUM_ROLE_MARKER, APP_HEALTH
from task.models import Task


class WeightView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView, Context):
    template_name = "health/chart.html"
    permission_required = 'task.view_health'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(APP_HEALTH)

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
        self.set_config(APP_HEALTH)

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
        self.set_config(APP_HEALTH)

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
def get_data_from_db(user_id: int, name, period: ChartPeriod=None, filter=None) -> list:
    src_data: list[SourceData] = []
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
        case 'temp':
            data = Task.objects.filter(user=user_id, app_health=NUM_ROLE_MARKER).exclude(bio_temp=None).exclude(bio_temp=0).order_by('event')
            if filter:
                filter_id = int(filter)
                if filter_id:
                    incident = Task.objects.filter(id=filter_id).get()
                    if incident.start:
                        data = data.filter(event__gte=incident.start)
                    if incident.stop:
                        data = data.filter(event__lte=incident.stop)
            src_data = [SourceData(event=x.event, value=Decimal(x.bio_temp)) for x in data if x.event and x.bio_temp]

    chart_points = approximate(src_data, 200)
    return chart_points

#----------------------------------
def build_weight_chart(user_id: int, period: ChartPeriod):
    chart_points = get_data_from_db(user_id, 'weight', period)
    chart_config = build_chart_config('Weight, kg', chart_points, '255, 99, 132')
    widget_data = {
        'chart': chart_config,
    }
    return widget_data

def get_api_health_chart(period: ChartPeriod):
    api_url = settings.DJANGO_HOST_LOG
    service_token = settings.DJANGO_SERVICE_TOKEN
    headers = {'Authorization': 'Token ' + service_token, 'User-Agent': 'Mozilla/5.0'}
    verify = settings.DJANGO_CERT
    resp = requests.get(api_url + '/api/get_chart_data?mark=health&period=' + period.value, headers=headers, verify=verify)
    if (resp.status_code != 200):
        return None
    return json.loads(resp.content)

def build_health_chart(user_id: int, period: ChartPeriod):
    if settings.DJANGO_DEVICE != settings.DJANGO_LOG_DEVICE:
        ret = get_api_health_chart(period)
        if ret:
            return ret
    chart_points = get_data_from_db(user_id, 'weight', period)
    current = change = None
    if chart_points:
        current = chart_points[-1]['y']
        change = chart_points[-1]['y'] - chart_points[0]['y']
    chart_config = build_chart_config('Weight, kg', chart_points, '255, 99, 132')
    widget_data = {
        'chart': chart_config,
        'current': current,
        'change': change,
    }
    return widget_data



def build_waist_chart(user_id: int):
    chart_points = get_data_from_db(user_id, 'waist')
    chart_config = build_chart_config('Waist, cm', chart_points, '111, 184, 71')
    widget_data = {
        'chart': chart_config,
    }
    return widget_data

def build_temp_chart(user_id: int, filter):
    chart_points = get_data_from_db(user_id, 'temp', filter=filter)
    chart_config = build_chart_config('Temperature, °C', chart_points, '111, 99, 255')
    widget_data = {
        'chart': chart_config,
    }
    return widget_data

def get_health_data(user_id: int, mark: str, period: ChartPeriod, filter=None):
    data = {}
    match mark:
        case 'weight': data = build_weight_chart(user_id, period)
        case 'waist': data = build_waist_chart(user_id)
        case 'temp': data = build_temp_chart(user_id, filter)
        case 'health': data = build_health_chart(user_id, period)
    return data