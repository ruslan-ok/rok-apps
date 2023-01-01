from datetime import timedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from task.const import ROLE_CAR, ROLE_APP
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView
from fuel.forms.car import CreateForm, EditForm
from fuel.config import app_config

role = ROLE_CAR
app = ROLE_APP[role]

class ListView(LoginRequiredMixin, BaseListView):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)


class DetailView(LoginRequiredMixin, BaseDetailView):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        get_info(form.instance)
        return response

def get_info(item):
    attr = []
    if item.car_plate:
        attr.append({'text': item.car_plate})
    item.actualize_role_info(app, role, attr)

def get_new_odometr(user, car, event):
    lag = event - timedelta(150)
    last = Task.objects.filter(user=user.id, app_fuel__gt=0, task_1=car.id, event__gt=lag).exclude(car_odometr=None).exclude(car_odometr=0).order_by('-event')
    new_odo = 0
    if (len(last) == 1):
        new_odo = last[0].car_odometr
    elif (len(last) > 1):
        qnt = len(last) - 1
        fix_days = (last[0].event - last[qnt].event).days
        per_days = (event - last[0].event).days
        new_odo = last[0].car_odometr
        if fix_days:
            new_odo = last[0].car_odometr + (last[0].car_odometr - last[qnt].car_odometr) / fix_days * per_days
    return new_odo

