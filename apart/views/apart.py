from datetime import date, datetime
from django.utils.translation import gettext_lazy as _
from task.const import ROLE_APART, NUM_ROLE_APART
from task.models import Task, TaskGroup, Urls, Step
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView, get_app_doc
from apart.forms.apart import CreateForm, EditForm
from apart.config import app_config
from apart.models import Apart

role = ROLE_APART

class TuneData:
    def tune_dataset(self, data, view_mode):
        return data;

class ListView(BaseListView, TuneData):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_APART
        response = super().form_valid(form)
        Apart.objects.create(user=form.instance.user, task=form.instance, name=form.instance.name);
        return response

    def get_info(self, item):
        ret = []
        return ret

class DetailView(BaseDetailView, TuneData):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        if Apart.objects.filter(task=form.instance.id).exists():
            apart = Apart.objects.filter(task=form.instance.id).get()
            apart.has_el = form.cleaned_data['has_el']
            apart.has_hw = form.cleaned_data['has_hw']
            apart.has_cw = form.cleaned_data['has_cw']
            apart.has_gas = form.cleaned_data['has_gas']
            apart.has_ppo = form.cleaned_data['has_ppo']
            apart.save()
        return response


def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)
