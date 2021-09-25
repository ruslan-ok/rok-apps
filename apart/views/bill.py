from datetime import date, datetime
from django.utils.translation import gettext_lazy as _
from task.const import ROLE_BILL
from task.models import Task, TaskGroup, Urls, Step
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView, get_app_doc
from apart.forms.bill import CreateForm, EditForm
from apart.config import app_config

role = ROLE_BILL

class TuneData:
    def tune_dataset(self, data, view_mode):
        return data;

class ListView(BaseListView, TuneData):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_info(self, item):
        ret = []
        return ret

class DetailView(BaseDetailView, TuneData):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)
