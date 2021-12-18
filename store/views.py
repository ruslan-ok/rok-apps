from task.const import ROLE_STORE, NUM_ROLE_STORE, ROLE_APP
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView, get_app_doc
from store.forms import CreateForm, EditForm
from store.config import app_config
from store.get_info import get_info

role = ROLE_STORE
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
        form.instance.set_item_attr(app, get_info(form.instance))
        return response


class GroupView(BaseGroupView, TuneData):
    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)

