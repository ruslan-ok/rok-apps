from task.const import ROLE_WARR, ROLE_APP
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView
from rusel.base.forms import GroupForm
from warr.forms import CreateForm, EditForm
from warr.config import app_config

role = ROLE_WARR
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

class GroupView(BaseGroupView, TuneData):
    form_class = GroupForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

