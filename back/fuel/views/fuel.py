import json
from datetime import datetime
from task.const import ROLE_FUEL, ROLE_APP, NUM_ROLE_FUEL
from task.models import Task
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import FormView
from core.views import BaseListView, BaseDetailView
from core.context import Context
from fuel.forms.fuel import CreateForm, EditForm
from fuel.fuel_get_info import get_info

role = ROLE_FUEL
app = ROLE_APP[role]

class ListView(LoginRequiredMixin, PermissionRequiredMixin, BaseListView):
    model = Task
    form_class = CreateForm
    permission_required = 'task.view_fuel'

    def __init__(self):
        super().__init__(app)

    def get(self, request):
        view = request.GET.get('view', '')
        if view == 'map':
            return FuelMapView.as_view()(request) 
        ret = super().get(request)
        return ret


class DetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView):
    model = Task
    form_class = EditForm
    permission_required = 'task.change_fuel'

    def __init__(self):
        super().__init__(app)

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.name = get_item_name(form.instance.event)
        form.instance.save()
        get_info(form.instance)
        return response

def get_item_name(event):
    name = event.strftime('%Y.%m.%d')
    return name

def add_fuel(user, car):
    counter_max = counter_min = total_volume = 0
    #TODO: optimize
    fuels = Task.objects.filter(user=user.id, app_fuel=NUM_ROLE_FUEL, task_1=car.id).order_by('-event')
    for f in fuels:
        counter_min = f.car_odometr
        if (counter_max == 0):
            counter_max = f.car_odometr
        else:
            total_volume += f.fuel_volume
    km = counter_max - counter_min
    if (total_volume == 0) or (km == 0):
        consumption = 0
    consumption = round((total_volume / km) * 100, 2)

    new_odo = new_prc = 0
    if (len(fuels) == 0):
        new_vol = 25
    else:
        new_vol = fuels[0].fuel_volume
        new_prc = fuels[0].fuel_price
        if (len(fuels) > 2):
            if (fuels[0].fuel_volume != fuels[1].fuel_volume) and (fuels[1].fuel_volume == fuels[2].fuel_volume):
                new_vol = fuels[1].fuel_volume
                new_prc = fuels[1].fuel_price
        if consumption:
            new_odo = fuels[0].car_odometr + int(fuels[0].fuel_volume / consumption * 100)
    event=datetime.now()
    task = Task.objects.create(user=user, app_fuel=NUM_ROLE_FUEL, task_1=car, event=event, name=get_item_name(event), car_odometr=new_odo, fuel_volume=new_vol, fuel_price=new_prc)
    return task

class FuelMapView(LoginRequiredMixin, PermissionRequiredMixin, Context, FormView):
    model = Task
    form_class = CreateForm
    template_name = 'fuel/map.html'
    permission_required = 'task.view_fuel'

    def __init__(self):
        super().__init__()
        self.set_config(app)

    def get_context_data(self):
        self.config.set_view(self.request)
        context = super().get_context_data()
        context.update(self.get_app_context(self.request.user.id))
        tasks = Task.objects.filter(user=self.request.user.id).exclude(app_fuel=0).exclude(latitude=None).exclude(longitude=None)
        gps_data = []
        for task in tasks:
            gps_data.append({
                'name': task.name,
                'url': task.get_absolute_url(),
                'lat': task.latitude,
                'lon': task.longitude,
            })
        context['gps_data'] = json.dumps(gps_data)
        return context
