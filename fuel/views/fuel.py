from datetime import datetime
from task.const import ROLE_FUEL, ROLE_APP, NUM_ROLE_FUEL
from task.models import Task
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from rusel.base.views import BaseListView, BaseDetailView
from fuel.forms.fuel import CreateForm, EditForm
from fuel.config import app_config

role = ROLE_FUEL
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

def get_info(item):
    attr = []
    attr.append({'text': _('odometr: ') + '{:,}'.format(item.car_odometr)})
    attr.append({'text': _('volume: ') + '{:.0f}'.format(item.fuel_volume)})
    attr.append({'text': _('price: ') + '{:.2f}'.format(item.fuel_price)})
    attr.append({'text': _('summa: ') + '{:.2f}'.format(item.fuel_volume * item.fuel_price)})
    item.actualize_role_info(app, role, attr)

