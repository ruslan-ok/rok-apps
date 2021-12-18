from task.const import ROLE_MARKER, ROLE_APP
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView
from health.forms import CreateForm, EditForm, IncidentForm
from health.config import app_config

role = ROLE_MARKER
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

class IncidentView(BaseGroupView, TuneData):
    form_class = IncidentForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

