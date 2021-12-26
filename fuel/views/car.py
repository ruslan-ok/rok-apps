from task.const import ROLE_CAR, ROLE_APP
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView
from fuel.forms.car import CreateForm, EditForm
from fuel.config import app_config

role = ROLE_CAR
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

    if item.info:
        info_descr = item.info[:80]
        if len(item.info) > 80:
            info_descr += '...'
        attr.append({'icon': 'notes', 'text': info_descr})

    ret = {'attr': attr}
    return ret
