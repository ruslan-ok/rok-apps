from task.const import ROLE_DOC
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView, get_app_doc
from docs.forms import CreateForm, EditForm
from docs.config import app_config

role = ROLE_DOC

class ListView(BaseListView):
    model = Task
    form_class = CreateForm

    def __init__(self, role, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)


class DetailView(BaseDetailView):
    model = Task
    form_class = EditForm

    def __init__(self, role, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

class GroupView(BaseGroupView):

    def __init__(self, role, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)
