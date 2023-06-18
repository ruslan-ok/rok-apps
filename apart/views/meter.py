from datetime import date, datetime
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from task.const import APP_APART, ROLE_METER, NUM_ROLE_METER, NUM_ROLE_BILL, NUM_ROLE_METER_VALUE
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView
from apart.forms.meter import CreateForm, EditForm
from apart.config import app_config

app = APP_APART
role = ROLE_METER

class ListView(LoginRequiredMixin, PermissionRequiredMixin, BaseListView):
    model = Task
    form_class = CreateForm
    permission_required = 'task.view_apart'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_queryset(self):
        data = super().get_queryset()
        query = None
        if (self.request.method == 'GET'):
            query = self.request.GET.get('q')
        if not data or query:
            return data
        return data[:12]

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_METER
        response = super().form_valid(form)
        return response

class DetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView):
    model = Task
    form_class = EditForm
    permission_required = 'task.change_apart'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_question'] = _('delete meters data').capitalize()
        if Task.objects.filter(app_apart=NUM_ROLE_BILL, task_2=self.object.id).exists() or Task.objects.filter(app_apart=NUM_ROLE_BILL, task_3=self.object.id).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because there are bills for this meters data').capitalize()
        if Task.objects.filter(app_apart=NUM_ROLE_METER, task_1=self.object.task_1.id, start__gt=self.object.start).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because there is an entry with a higher date').capitalize()
        context['apart_meters'] = Task.objects.filter(app_apart=NUM_ROLE_METER_VALUE, task_1=self.object.task_1.id, start=self.object.start)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.name = get_meter_name(form.instance.start)
        form.instance.save()
        get_info(form.instance)
        return response

def get_info(item):
    ret = []
    if (item.task_1.apart_has_el):
        ret.append({'text': '{} {}'.format(_('el:'), item.meter_el)})
    if (item.task_1.apart_has_hw):
        ret.append({'text': '{} {}'.format(_('hw:'), item.meter_hw)})
    if (item.task_1.apart_has_cw):
        ret.append({'text': '{} {}'.format(_('cw:'), item.meter_cw)})
    if (item.task_1.apart_has_gas):
        ret.append({'text': '{} {}'.format(_('gas:'), item.meter_ga)})
    item.actualize_role_info(app, role, ret)

#----------------------------------
def next_period(last=None):
    if not last:
        y = datetime.now().year
        m = datetime.now().month
        if (m == 1):
            m = 12
            y = y - 1
        else:
            m = m - 1
    else:
        y = last.year
        m = last.month
        
        if (m == 12):
            y = y + 1
            m = 1
        else:
            m = m + 1

    return date(y, m, 1)

def get_meter_name(period):
    return period.strftime('%Y.%m')

def add_meter(user, apart):
    few = Task.objects.filter(app_apart=NUM_ROLE_METER, task_1=apart.id).order_by('-start')[:3]
    qty = len(few)
    if (qty == 0):
        period = next_period()
        el = 0
        hw = 0
        cw = 0
        ga = 0
    else:
        last = few[0]
        period = next_period(last.start)

        el = last.meter_el
        hw = last.meter_hw
        cw = last.meter_cw
        ga = last.meter_ga

        if (qty > 1):
            first = few[qty-1]
            el = last.meter_el + round((last.meter_el - first.meter_el) / (qty - 1))
            hw = last.meter_hw + round((last.meter_hw - first.meter_hw) / (qty - 1))
            cw = last.meter_cw + round((last.meter_cw - first.meter_cw) / (qty - 1))
            if last.meter_ga:
                ga = last.meter_ga + round((last.meter_ga - first.meter_ga) / (qty - 1))

    task = Task.objects.create(user=user, app_apart=NUM_ROLE_METER, event=datetime.now(), task_1=apart, start=period, name=get_meter_name(period), meter_el=el, meter_hw=hw, meter_cw=cw, meter_ga=ga)
    return task
