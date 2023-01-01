from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from task.const import NUM_ROLE_PART, NUM_ROLE_SERVICE, ROLE_SERVICE, ROLE_APP, APP_FUEL
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView
from fuel.forms.serv import CreateForm, EditForm
from fuel.views.car import get_new_odometr
from fuel.config import app_config

role = ROLE_SERVICE
app = ROLE_APP[role]

class ListView(LoginRequiredMixin, BaseListView):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_template_names(self):
        return ['fuel/list.html']


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_item_template'] = 'fuel/add_service.html'
        nav_item = Task.get_active_nav_item(self.request.user.id, APP_FUEL)
        form = CreateForm(nav_item, self.request.user.id)
        context['form'] = form
        return context

class DetailView(LoginRequiredMixin, BaseDetailView):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.name = get_item_name(form.instance.task_2, form.instance.event)
        form.instance.save()
        get_info(form.instance)
        return response

def get_info(item):
    attr = []
    attr.append({'text': _('odometr: ') + '{:,}'.format(item.car_odometr)})
    if item.repl_manuf:
        attr.append({'text': item.repl_manuf})
    if item.repl_part_num:
        attr.append({'text': item.repl_part_num})
    if item.repl_descr:
        attr.append({'text': item.repl_descr})
    item.actualize_role_info(app, role, attr)

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
