from task.const import ROLE_DOC, ROLE_APP
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView
from docs.forms import CreateForm, EditForm, FolderForm
from docs.config import app_config

role = ROLE_DOC
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

class FolderView(BaseGroupView, TuneData):
    form_class = FolderForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

