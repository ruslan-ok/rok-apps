from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from task import const
from task.models import Task
from core.views import BaseListView, BaseDetailView
from fuel.forms.part import CreateForm, EditForm
from fuel.config import app_config
from fuel.utils import month_declination

role = const.ROLE_PART
app = const.ROLE_APP[role]

class ListView(LoginRequiredMixin, PermissionRequiredMixin, BaseListView):
    model = Task
    form_class = CreateForm
    permission_required = 'task.view_fuel'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_template_names(self):
        return ['fuel/list.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nav_role = Task.get_active_nav_item(self.request.user.id, app)
        if nav_role:
            if Task.objects.filter(user=self.request.user.id, app_fuel__gt=0, task_1=nav_role.id).exclude(car_odometr=None).exclude(car_odometr=0).exists():
                last_odo = Task.objects.filter(user=self.request.user.id, app_fuel__gt=0, task_1=nav_role.id).exclude(car_odometr=None).exclude(car_odometr=0).order_by('-event')[0]
                href = last_odo.get_absolute_url()
                match last_odo.app_fuel:
                    case const.NUM_ROLE_FUEL: operation = 'fueling'
                    case const.NUM_ROLE_SERVICE: operation = 'service'
                    case _: operation = '???'

                value = 'Last operation: ' + operation + ' on ' + last_odo.event.strftime('%d.%m.%Y') + ', odometer ' + str(last_odo.car_odometr)
                context.update({'summary': [{'color': 'black', 'value': value, 'href': href}]})
        return context


class DetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView):
    model = Task
    form_class = EditForm
    permission_required = 'task.change_fuel'

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
    task = Task.objects.create(user=user, app_fuel=const.NUM_ROLE_PART, name=name, event=datetime.now(), task_1=car, part_chg_km=10000, part_chg_mo=12)
    return task
