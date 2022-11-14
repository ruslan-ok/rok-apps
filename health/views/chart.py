import json
from datetime import datetime
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
        data = build_weight_chart(self.request.user)
        s_data = json.dumps(data)
        context['chart_data'] = s_data
        context['title'] = _('Weight measurement chart')
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
        data = build_waist_chart(self.request.user)
        s_data = json.dumps(data)
        context['chart_data'] = s_data
        context['title'] = _('Waist measurement chart')
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
        data = build_temp_chart(self.request.user)
        s_data = json.dumps(data, default=str)
        context['chart_data'] = s_data
        context['title'] = _('Temperature chart')
        context['hide_add_item_input'] = True
        return context

#----------------------------------
def get_data_from_db(user, name, compact=False):
    x = []
    y = []
    min_value = max_value = min_date = max_date = last_value = None

    if (name == 'weight'):
        data = Task.objects.filter(user=user.id, app_health=NUM_ROLE_MARKER).exclude(bio_weight=None).exclude(bio_weight=0).order_by('event')
        if (len(data) > 0):
            values = Task.objects.filter(user=user.id, app_health=NUM_ROLE_MARKER).exclude(bio_weight=None).exclude(bio_weight=0).order_by('bio_weight')
            min_value = values[0].bio_weight
            max_value = values[len(values)-1].bio_weight
            min_date = values[0].event.date()
            max_date = values[len(values)-1].event.date()
            if compact:
                min_date = max_date.replace(year=(max_date.year-1))
            last_value = data[len(data)-1].bio_weight
    elif (name == 'waist'):
        data = Task.objects.filter(user=user.id, app_health=NUM_ROLE_MARKER).exclude(bio_waist=None).exclude(bio_waist=0).order_by('event')
        if (len(data) > 0):
            values = Task.objects.filter(user=user.id, app_health=NUM_ROLE_MARKER).exclude(bio_waist=None).exclude(bio_waist=0).order_by('bio_waist')
            min_value = values[0].bio_waist
            max_value = values[len(values)-1].bio_waist
            min_date = values[0].event.date()
            max_date = values[len(values)-1].event.date()
            last_value = data[len(data)-1].bio_waist
    else:
        data = []
    
    cur_day = average = qty = None
    for b in data:
        work_date = b.event.date()
        if work_date < min_date:
            continue
        if cur_day and (cur_day == work_date):
            qty += 1
            if (name == 'weight'):
                average += b.bio_weight
            elif (name == 'waist'):
                average += b.bio_waist
        else:
            if cur_day:
                x.append(cur_day)
                if (cur_day == min_date):
                    y.append(min_value)
                elif (cur_day == max_date):
                    y.append(max_value)
                else:
                    y.append(average / qty)
            qty = 1
            cur_day = work_date
            if (name == 'weight'):
                average = b.bio_weight
            elif (name == 'waist'):
                average = b.bio_waist
    
    return x, y, min_value, max_value, min_date, max_date, last_value

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

def build_weight_chart(user, compact=False):
    x, y, min_value, max_value, min_date, max_date, last_vaue = get_data_from_db(user, 'weight', compact=compact)
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

def build_waist_chart(user):
    x, y, min_value, max_value, min_date, max_date, last_vaue = get_data_from_db(user, 'waist')
    x, y = approximate_months(x, y)

    data = {
        'type': 'line',
        'data': {'labels': x,
            'datasets': [{
                'label': 'Waist, cm',
                'data': y,
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1,
                'tension': 0.4,
            }]
        },
    }
    return data

def build_temp_chart(user):
    x = []
    y = []
    values = Task.objects.filter(user=user.id, app_health=NUM_ROLE_MARKER).exclude(bio_temp=None).order_by('event')
    for t in values:
        x.append(t.event.strftime('%Y-%m-%dT%H:%M'))
        y.append(t.bio_temp)

    data = {
        'type': 'line',
        'data': {'labels': x,
            'datasets': [{
                'label': 'Temperature, °C',
                'data': y,
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1,
                'tension': 0.4,
            }]
        },
        'options': {
            'scales': {
                'xAxis': {
                    'type': 'time'
                }
            }
        }
    }
    return data
