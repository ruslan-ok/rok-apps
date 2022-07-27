from django.contrib.auth.mixins import LoginRequiredMixin
from task.const import ROLE_NOTE, ROLE_APP
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView
from note.forms import CreateForm, EditForm
from note.config import app_config
from note.get_info import get_info

role = ROLE_NOTE
app = ROLE_APP[role]

class TuneData:
    def tune_dataset(self, data, group):
        return data

class ListView(LoginRequiredMixin, BaseListView, TuneData):
    model = Task
    form_class = CreateForm
    login_url = '/account/login/'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)


class DetailView(LoginRequiredMixin, BaseDetailView, TuneData):
    model = Task
    form_class = EditForm
    login_url = '/account/login/'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.set_item_attr(app, get_info(form.instance))
        return response


class GroupView(LoginRequiredMixin, BaseGroupView, TuneData):
    login_url = '/account/login/'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
