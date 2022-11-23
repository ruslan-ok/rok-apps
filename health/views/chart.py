from decimal import Decimal
from datetime import datetime, timedelta
from django.http import Http404
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
from rusel.base.views import Context
from health.config import app_config
from task.const import NUM_ROLE_MARKER, ROLE_CHART_WEIGHT, ROLE_CHART_WAIST, ROLE_CHART_TEMP
from task.models import Task

class WeightView(TemplateView, Context):
    template_name = "health/chart.html"

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

class WaistView(TemplateView, Context):
    template_name = "health/chart.html"

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

class TempView(TemplateView, Context):
    template_name = "health/chart.html"

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
        return context

#----------------------------------
def get_data_from_db(user_id: int, name):
    x = []
    y = []

    match name:
        case 'weight': data = Task.objects.filter(user=user_id, app_health=NUM_ROLE_MARKER).exclude(bio_weight=None).exclude(bio_weight=0).order_by('event')
        case 'waist': data = Task.objects.filter(user=user_id, app_health=NUM_ROLE_MARKER).exclude(bio_waist=None).exclude(bio_waist=0).order_by('event')
        case _: data = []
    
    cur_day = None
    average = Decimal(0)
    qty: int = 0
    for b in data:
        work_date = b.event.date()
        if cur_day and (cur_day == work_date):
            qty += 1
            match name:
                case 'weight' : w = b.bio_weight
                case 'waist': w = b.bio_waist
                case _: w = 0
            average += w
        else:
            if cur_day:
                x.append(cur_day)
                y.append(average / qty)
            qty = 1
            cur_day = work_date
            match name:
                case 'weight' : average = b.bio_weight
                case 'waist': average = b.bio_waist
                case _: average = 0
    
    return x, y

#----------------------------------
def approximate_months(x, y):
    ret_x = []
    ret_y = []
    cur_period = None
    qty = average = 0
    for i in range(len(y)):
        period = str(x[i].year) + '.' + str(x[i].month)
        if cur_period and (cur_period == period):
            qty += 1
            average += y[i]
        else:
            if cur_period:
                ret_x.append(cur_period)
                value = round(average / qty, 1)
                ret_y.append(str(value))
            qty = 1
            cur_period = period
            average = y[i]
    return ret_x, ret_y

def build_weight_chart(user_id: int):
    x, y = get_data_from_db(user_id, 'weight')
    x, y = approximate_months(x, y)

    data = {
        'type': 'line',
        'data': {'labels': x,
            'datasets': [{
                'label': 'Weight, kg',
                'data': y,
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1,
                'tension': 0.4,
            }]
        },
    }
    return data

def build_health_chart(user_id: int):
    x = []
    y = []
    values = Task.objects.filter(user=user_id, app_health=NUM_ROLE_MARKER).exclude(bio_weight=None).exclude(bio_weight=0).order_by('-event')
    if len(values) > 0:
        last_dt = values[0].event.date()
        start_dt = last_dt - timedelta(30)
        values = Task.objects.filter(user=user_id, app_health=NUM_ROLE_MARKER, event__gt=start_dt).exclude(bio_weight=None).exclude(bio_weight=0).order_by('event')
        for t in values:
            x.append(t.event.strftime('%m-%d'))
            y.append(t.bio_weight)

    data = {
        'type': 'line',
        'data': {'labels': x,
            'datasets': [{
                'label': 'Weight, kg',
                'data': y,
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
    x, y = get_data_from_db(user_id, 'waist')
    x, y = approximate_months(x, y)

    data = {
        'type': 'line',
        'data': {'labels': x,
            'datasets': [{
                'label': 'Waist, cm',
                'data': y,
                'backgroundColor': 'rgba(111, 184, 71, 0.2)',
                'borderColor': 'rgba(111, 184, 71, 1)',
                'borderWidth': 1,
                'tension': 0.4,
            }]
        },
    }
    return data

def build_temp_chart(user_id: int):
    x = []
    y = []
    values = Task.objects.filter(user=user_id, app_health=NUM_ROLE_MARKER).exclude(bio_temp=None).exclude(bio_temp=0).order_by('event')
    for t in values:
        x.append(t.event.strftime('%Y-%m-%d'))
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
                    'display': False,
                }
            }
        }
    }
    return data

def get_chart_data(user_id: int, mark: str):
    data = {}
    match mark:
        case 'weight': data = build_weight_chart(user_id)
        case 'waist': data = build_waist_chart(user_id)
        case 'temp': data = build_temp_chart(user_id)
        case 'health': data = build_health_chart(user_id)
    return data