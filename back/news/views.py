from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from task.const import APP_NEWS, ROLE_NEWS
from task.models import Task
from core.views import BaseListView, BaseDetailView, BaseGroupView
from news.forms import CreateForm, EditForm
from news.config import app_config
from news.get_info import get_info

app = APP_NEWS
role = ROLE_NEWS

class ListView(LoginRequiredMixin, PermissionRequiredMixin, BaseListView):
    model = Task
    form_class = CreateForm
    permission_required = 'task.view_news'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)


class DetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView):
    model = Task
    form_class = EditForm
    permission_required = 'task.change_news'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        get_info(form.instance)
        return response


class GroupView(LoginRequiredMixin, BaseGroupView):

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
