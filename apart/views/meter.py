from datetime import date, datetime
from django.utils.translation import gettext_lazy as _
from task.const import ROLE_METER, NUM_ROLE_METER
from task.models import Task, TaskGroup, Urls, Step
from rusel.base.views import BaseDetailView, BaseGroupView, get_app_doc
from apart.views.base_list import BaseApartListView
from apart.forms.meter import CreateForm, EditForm
from apart.config import app_config
from apart.models import Meter, Apart

role = ROLE_METER

class TuneData:
    def tune_dataset(self, data, view_mode):
        return data

class ListView(BaseApartListView, TuneData):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def transform_datalist(self, items):
        apart = Apart.objects.filter(user=self.request.user, active=True).get()
        tasks = []
        for t in items.order_by('-name'):
            meter = Meter.objects.filter(task=t.id).get()
            if (meter.apart.id != apart.id):
                continue
            item = {
                'id': t.id,
                'name': self.get_task_name(t),
                'attrs': self.get_info(t)
            }
            tasks.append(item)
        return tasks

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_METER
        response = super().form_valid(form)
        return response

    def get_task_name(self, task):
        meter = Meter.objects.filter(task=task.id).get()
        return meter.period.strftime('%m.%Y')

    def get_info(self, item):
        meter = Meter.objects.filter(task=item.id).get()
        ret = []
        ret.append({'text': '{} {}'.format(_('el:'), meter.el)})
        ret.append({'icon': 'separator'})
        ret.append({'text': '{} {}'.format(_('hw:'), meter.hw)})
        ret.append({'icon': 'separator'})
        ret.append({'text': '{} {}'.format(_('cw:'), meter.cw)})
        if (meter.apart.has_gas):
            ret.append({'icon': 'separator'})
            ret.append({'text': '{} {}'.format(_('ga:'), meter.ga)})
        return ret

class DetailView(BaseDetailView, TuneData):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)
