from django.contrib.auth.mixins import LoginRequiredMixin
from task.const import APP_NEWS, ROLE_NEWS
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView
from news.forms import CreateForm, EditForm
from news.config import app_config
from news.get_info import get_info

app = APP_NEWS
role = ROLE_NEWS

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
