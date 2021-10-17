from django.utils.translation import gettext_lazy as _
from task.const import APP_TODO, ROLE_TODO, NUM_ROLE_TODO
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView, get_app_doc
from todo.forms import CreateForm, EditForm
from todo.config import app_config
from todo.get_info import get_info

app = APP_TODO
role = ROLE_TODO

class TuneData:
    def tune_dataset(self, data, view_mode):
        if (view_mode == 'todo'):
            return data.filter(in_my_day=True).exclude(completed=True)
        if (view_mode == 'important'):
            return data.filter(important=True).exclude(completed=True)
        if (view_mode == 'planned'):
            return data.exclude(stop=None).exclude(completed=True)
        if (view_mode == 'completed'):
            return data.filter(completed=True)
        return data;

class ListView(BaseListView, TuneData):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        form.instance.app_task = NUM_ROLE_TODO
        response = super().form_valid(form)
        return response

class DetailView(BaseDetailView, TuneData):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.set_item_attr(app, get_info(form.instance))
        return response


class GroupView(BaseGroupView, TuneData):
    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)
