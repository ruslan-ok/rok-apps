from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from rusel.base.views import BaseListView, BaseDetailView
from health.forms.marker import CreateForm, EditForm
from task.const import ROLE_MARKER, ROLE_APP, NUM_ROLE_MARKER
from task.models import Task
from health.config import app_config

role = ROLE_MARKER
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
        form.instance.name = get_item_name(self.request.user.id, form.instance.event, form.instance.id)
        form.instance.save()
        form.instance.set_item_attr(app, get_info(form.instance))
        return response

def get_item_name(user_id, event, id=None):
    name = event.strftime('%Y.%m.%d')
    if id:
        this_day = Task.objects.filter(user=user_id, 
                                        app_health=NUM_ROLE_MARKER, 
                                        event__year=event.year, 
                                        event__month=event.month, 
                                        event__day=event.day, 
                                        ).exclude(id=id)
    else:
        this_day = Task.objects.filter(user=user_id, 
                                        app_health=NUM_ROLE_MARKER, 
                                        event__year=event.year, 
                                        event__month=event.month, 
                                        event__day=event.day, 
                                        )
    if len(this_day):
        name = event.strftime('%Y.%m.%d - %H:%M')
        for x in this_day:
            x.name = x.event.strftime('%Y.%m.%d - %H:%M')
            x.save()
    return name

def get_info(item):
    attr = []

    if item.bio_height:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        attr.append({'icon': 'myday', 'text': '{}: {} {}'.format(_('Height'), item.bio_height, _('cm')) })

    if item.bio_weight:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        attr.append({'icon': 'myday', 'text': '{}: {} {}'.format(_('Weight'), item.bio_weight, _('kg')) })

    if item.bio_temp:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        attr.append({'icon': 'myday', 'text': '{}: {}'.format(_('Temperature'), item.bio_temp) })

    if item.bio_waist:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        attr.append({'icon': 'myday', 'text': '{}: {} {}'.format(_('Waist'), item.bio_waist, _('cm')) })

    if item.bio_systolic or item.bio_diastolic:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        attr.append({'icon': 'myday', 'text': '{}: {}/{}'.format(_('Pressure'), item.bio_systolic, item.bio_diastolic) })

    if item.bio_pulse:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        attr.append({'icon': 'myday', 'text': '{}: {}'.format(_('Pulse'), item.bio_pulse) })

    if item.info:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        info_descr = item.info[:80]
        if len(item.info) > 80:
            info_descr += '...'
        attr.append({'icon': 'notes', 'text': info_descr})

    ret = {'attr': attr}
    return ret

def add_item(user, value):
    height = None
    weight = None
    temp = None
    waist = None
    systolic = None
    diastolic = None
    pulse = None
    info = ''
    n_value = 0

    try:
        n_value = float(value.replace(',', '.'))
    except ValueError:
        info = value

    if (n_value >= 35) and (n_value < 50):
        temp = n_value
    elif (n_value >= 50) and (n_value < 90):
        weight = n_value
    elif (n_value >= 90) and (n_value < 150):
        waist = n_value
    elif (n_value >= 150) and (n_value < 250):
        height = n_value

    event = datetime.now()
    name = get_item_name(user.id, event)
    task = Task.objects.create(user=user, app_health=NUM_ROLE_MARKER, name=name, bio_height=height, bio_weight=weight, bio_temp=temp, bio_waist=waist, \
                                bio_systolic=systolic, bio_diastolic=diastolic, bio_pulse=pulse, info=info, event=event)
    task.set_item_attr(app, get_info(task))
    return task

