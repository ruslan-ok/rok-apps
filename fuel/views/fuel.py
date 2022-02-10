from datetime import datetime
from task.const import ROLE_FUEL, ROLE_APP, NUM_ROLE_FUEL
from task.models import Task, Urls
from django.utils.translation import gettext_lazy as _
from rusel.files import get_files_list, get_app_doc
from rusel.categories import get_categories_list
from rusel.base.views import BaseListView, BaseDetailView
from fuel.forms.fuel import CreateForm, EditForm
from fuel.config import app_config

role = ROLE_FUEL
app = ROLE_APP[role]

class TuneData:
    def tune_dataset(self, data, group):
        return data

class ListView(BaseListView, TuneData):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)


class DetailView(BaseDetailView, TuneData):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.name = get_item_name(form.instance.event)
        form.instance.save()
        form.instance.set_item_attr(app, get_info(form.instance))
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
    attr.append({'icon': 'separator'})
    attr.append({'text': _('volume: ') + '{:.0f}'.format(item.fuel_volume)})
    attr.append({'icon': 'separator'})
    attr.append({'text': _('price: ') + '{:.2f}'.format(item.fuel_price)})
    attr.append({'icon': 'separator'})
    attr.append({'text': _('summa: ') + '{:.2f}'.format(item.fuel_volume * item.fuel_price)})

    links = len(Urls.objects.filter(task=item.id)) > 0
    files = (len(get_files_list(item.user, app, role, item.id)) > 0)

    if item.info or links or files:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        if links:
            attr.append({'icon': 'url'})
        if files:
            attr.append({'icon': 'attach'})
        if item.info:
            info_descr = item.info[:80]
            if len(item.info) > 80:
                info_descr += '...'
            attr.append({'icon': 'notes', 'text': info_descr})

    if item.categories:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        categs = get_categories_list(item.categories)
        for categ in categs:
            attr.append({'icon': 'category', 'text': categ.name, 'color': 'category-design-' + categ.design})
    
    ret = {'attr': attr}
    return ret

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)

