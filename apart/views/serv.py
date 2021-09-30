from datetime import date, datetime
from django.utils.translation import gettext_lazy as _
from task.const import ROLE_SERVICE, NUM_ROLE_SERVICE
from task.models import Task, TaskGroup, Urls, Step
from rusel.base.views import BaseDetailView, BaseGroupView, get_app_doc
from apart.forms.serv import CreateForm, EditForm
from apart.config import app_config
from apart.models import Service, Apart
from apart.views.base_list import BaseApartListView

role = ROLE_SERVICE

class TuneData:
    def tune_dataset(self, data, view_mode):
        return data

class ListView(BaseApartListView, TuneData):
    model = Task
    form_class = CreateForm

    def transform_datalist(self, items):
        apart = Apart.objects.filter(user=self.request.user, active=True).get()
        tasks = []
        for t in items.order_by('-name'):
            if Service.objects.filter(task=t.id).exists():
                serv = Service.objects.filter(task=t.id).get()
                if (serv.apart.id != apart.id):
                    continue
            item = {
                'id': t.id,
                'name': self.get_task_name(t),
                'attrs': self.get_info(t)
            }
            tasks.append(item)
        return tasks

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_SERVICE
        response = super().form_valid(form)
        apart = Apart.objects.filter(user=form.instance.user, active=True).get()
        Service.objects.create(apart=apart, task=form.instance, name=form.instance.name);
        return response

    def get_info(self, item):
        ret = []
        ret.append({'text': item.info})
        return ret

class DetailView(BaseDetailView, TuneData):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)
