from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from task.const import NUM_ROLE_PART, ROLE_PART, ROLE_APP
from task.models import Task, Urls
from rusel.categories import get_categories_list
from rusel.base.views import BaseListView, BaseDetailView
from fuel.forms.part import CreateForm, EditForm
from fuel.config import app_config
from fuel.utils import month_declination

role = ROLE_PART
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
        self.template_name = 'fuel/list.html'


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

def get_info(item):
    attr = []

    if item.part_chg_km:
        attr.append({'text': '{} {}'.format(item.part_chg_km, _('km'))})

    if item.part_chg_mo:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        attr.append({'text': month_declination(item.part_chg_mo)})

    attr.append({'tuned_data': True})
    
    links = len(Urls.objects.filter(task=item.id)) > 0
    files = (len(item.get_files_list(role)) > 0)

    if item.info or links or files:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        if links:
            attr.append({'icon': 'url'})
        if files:
            attr.append({'icon': 'attach'})
        if item.info:
            info_descr = item.info[:80]
            if len(item.info) > 80:
                info_descr += '...'
            attr.append({'icon': 'notes', 'text': info_descr})

    if item.categories:
        if (len(attr) > 0):
            attr.append({'icon': 'separator'})
        categs = get_categories_list(item.categories)
        for categ in categs:
            attr.append({'icon': 'category', 'text': categ.name, 'color': 'category-design-' + categ.design})
    
    ret = {'attr': attr}

    return ret

def add_part(user, car, name):
    task = Task.objects.create(user=user, app_fuel=NUM_ROLE_PART, name=name, event=datetime.now(), task_1=car)
    return task
