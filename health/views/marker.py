from django.utils.translation import gettext_lazy as _
from rusel.base.views import BaseListView, BaseDetailView
from health.forms.marker import CreateForm, EditForm
from task.const import ROLE_MARKER, ROLE_APP
from task.models import Task
from health.config import app_config

role = ROLE_MARKER
app = ROLE_APP[role]

class TuneData:
    def tune_dataset(self, data, group):
        return data;

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
        form.instance.set_item_attr(app, get_info(form.instance))
        return response

def get_info(item):
    attr = []

    if item.bio_height:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        attr.append({'icon': 'myday', 'text': '{}: {} {}'.format(_('height').capitalize(), item.bio_height, _('cm')) })

    if item.bio_weight:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        attr.append({'icon': 'myday', 'text': '{}: {} {}'.format(_('weight').capitalize(), item.bio_weight, _('kg')) })

    if item.bio_temp:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        attr.append({'icon': 'myday', 'text': '{}: {}'.format(_('temperature').capitalize(), item.bio_temp) })

    if item.bio_waist:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        attr.append({'icon': 'myday', 'text': '{}: {} {}'.format(_('waist').capitalize(), item.bio_waist, _('cm')) })

    if item.bio_systolic or item.bio_diastolic:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        attr.append({'icon': 'myday', 'text': '{}: {}/{}'.format(_('pressure').capitalize(), item.bio_systolic, item.bio_diastolic) })

    if item.bio_pulse:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        attr.append({'icon': 'myday', 'text': '{}: {}'.format(_('pulse').capitalize(), item.bio_pulse) })

    if item.bio_info:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        attr.append({'icon': 'notes', 'text': item.bio_info })

    if item.info:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        info_descr = item.info[:80]
        if len(item.info) > 80:
            info_descr += '...'
        attr.append({'icon': 'notes', 'text': info_descr})

    ret = {'attr': attr}
    return ret
