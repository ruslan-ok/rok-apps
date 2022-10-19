from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from task.const import NUM_ROLE_PART, ROLE_PART, ROLE_APP
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView
from fuel.forms.part import CreateForm, EditForm
from fuel.config import app_config
from fuel.utils import month_declination

role = ROLE_PART
app = ROLE_APP[role]

class ListView(LoginRequiredMixin, BaseListView):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        self.template_name = 'fuel/list.html'


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
    if item.part_chg_km:
        attr.append({'text': '{} {}'.format(item.part_chg_km, _('km'))})
    if item.part_chg_mo:
        attr.append({'text': month_declination(item.part_chg_mo)})
    attr.append({'tuned_data': True})
    item.actualize_role_info(app, role, attr)

def add_part(user, car, name):
    task = Task.objects.create(user=user, app_fuel=NUM_ROLE_PART, name=name, event=datetime.now(), task_1=car)
    return task
