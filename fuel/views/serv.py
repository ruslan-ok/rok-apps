from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from task.const import NUM_ROLE_PART, NUM_ROLE_SERVICE, ROLE_SERVICE, ROLE_APP, APP_FUEL
from task.models import Task, Urls
from rusel.categories import get_categories_list
from rusel.base.views import BaseListView, BaseDetailView
from fuel.forms.serv import CreateForm, EditForm
from fuel.views.car import get_new_odometr
from fuel.config import app_config

role = ROLE_SERVICE
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


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_item_template'] = 'fuel/add_service.html'
        nav_item = Task.get_active_nav_item(self.request.user.id, APP_FUEL)
        form = CreateForm(nav_item, self.request.user.id)
        context['form'] = form
        return context

class DetailView(LoginRequiredMixin, BaseDetailView, TuneData):
    model = Task
    form_class = EditForm
    login_url = '/account/login/'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.name = get_item_name(form.instance.task_2, form.instance.event)
        form.instance.save()
        form.instance.set_item_attr(app, get_info(form.instance))
        return response

def get_info(item):
    attr = []

    attr.append({'text': _('odometr: ') + '{:,}'.format(item.car_odometr)})
    if item.repl_manuf:
        attr.append({'icon': 'separator'})
        attr.append({'text': item.repl_manuf})
    if item.repl_part_num:
        attr.append({'icon': 'separator'})
        attr.append({'text': item.repl_part_num})
    if item.repl_descr:
        attr.append({'icon': 'separator'})
        attr.append({'text': item.repl_descr})

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

def get_item_name(part, event):
    name = event.strftime('%Y.%m.%d')
    if part and part.name:
        name += ' ' + part.name
    return name

def add_serv(user, car, part_id):
    part = None
    if part_id:
        if Task.objects.filter(user=user.id, app_fuel=NUM_ROLE_PART, task_1=car.id, id=part_id).exists():
            part = Task.objects.filter(id=part_id).get()
    event = datetime.now()
    odometr = get_new_odometr(user, car, event)
    name = get_item_name(part, event)
    task = Task.objects.create(user=user, app_fuel=NUM_ROLE_SERVICE, name=name, event=event, task_1=car, task_2=part, car_odometr=odometr)
    return task
