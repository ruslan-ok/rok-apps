from task.const import ROLE_EXPENSE, NUM_ROLE_OPERATION, ROLE_APP
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView, get_app_doc
from expen.forms.expense import CreateForm, EditForm
from expen.config import app_config
from expen.get_info import get_info

role = ROLE_EXPENSE
app = ROLE_APP[role]

class TuneData:
    def tune_dataset(self, data, group):
        return data;

class ListView(BaseListView, TuneData):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        form.instance.app_expen = NUM_ROLE_OPERATION
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

