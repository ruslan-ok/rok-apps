from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from rusel.base.views import BaseListView, BaseDetailView
from health.forms.incident import CreateForm, EditForm
from task.const import ROLE_INCIDENT, ROLE_APP
from task.models import Task
from health.config import app_config

role = ROLE_INCIDENT
app = ROLE_APP[role]

class ListView(LoginRequiredMixin, BaseListView):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)


class DetailView(LoginRequiredMixin, BaseDetailView):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        get_info(form.instance)
        return response

def get_info(item):
    attr = []
    if item.start:
        attr.append({'text': '{} {}'.format(_('from'), item.start.strftime('%d.%m.%Y'))})
    if item.stop:
        attr.append({'text': '{} {}'.format(_('to'), item.stop.strftime('%d.%m.%Y'))})
    if item.diagnosis:
        attr.append({'text': item.diagnosis})
    item.actualize_role_info(app, role, attr)
