from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from task.const import APP_APART, ROLE_BILL, NUM_ROLE_BILL, NUM_ROLE_METER
from task.models import Task, Urls
from rusel.base.views import BaseListView, BaseDetailView
from apart.forms.bill import CreateForm, EditForm
from apart.config import app_config
from apart.views.meter import next_period
from apart.calc_tarif import HSC, INTERNET, PHONE, get_bill_info

app = APP_APART
role = ROLE_BILL

class ListView(LoginRequiredMixin, BaseListView):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_BILL
        response = super().form_valid(form)
        return response

class DetailView(LoginRequiredMixin, BaseDetailView):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        bill = self.get_object()
        if bill.task_2:
            context['prev'] = bill.task_2
        if bill.task_3:
            context['curr'] = bill.task_3
        if bill.task_2 and bill.task_3:
            context['bill_info'] = get_bill_info(bill)
        apart = bill.task_1
        context['apart_has_el'] = apart.apart_has_el
        context['apart_has_gas'] = apart.apart_has_gas
        context['apart_has_cw'] = apart.apart_has_cw
        context['apart_has_hw'] = apart.apart_has_hw
        context['tv_title'] = _('Interet/TV')
        context['phone_title'] = _('phone').capitalize()
        context['ZKX_title'] = _('HCS')
        context['PoO_title'] = _('PoO')
        context['delete_question'] = _('delete bill').capitalize()
        if Task.objects.filter(app_apart=NUM_ROLE_BILL, task_1=bill.task_1.id, start__gt=bill.start).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because it is not the last bill').capitalize()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.name = get_bill_name(form.instance.start)
        form.instance.save()
        form.instance.set_item_attr(app, get_info(form.instance))
        return response

def get_info(item):
    bill_info = get_bill_info(item)
    ret = []
    ret.append({'text': '{}: {}'.format(_('accrued'), bill_info['total']['accrued']) })
    ret.append({'icon': 'separator'})
    ret.append({'text': '{}: {}'.format(_('paid'), bill_info['total']['paid']) })

    links = len(Urls.objects.filter(task=item.id)) > 0
    files = len(item.get_files_list(role)) > 0

    if item.info or links or files:
        ret.append({'icon': 'separator'})
    if links:
        ret.append({'icon': 'url'})
    if files:
        ret.append({'icon': 'attach'})
    if item.info:
        info_descr = item.info[:80]
        if len(item.info) > 80:
            info_descr += '...'
        ret.append({'icon': 'notes', 'text': info_descr})
    return {'attr': ret}

def get_bill_name(period):
    return period.strftime('%Y.%m')

def avg_accrual(user, apart, period, service_id):
    last = Task.objects.filter(user=user.id, app_apart=NUM_ROLE_BILL, task_1=apart.id, start__lt=period).order_by('-start')[:3]
    ret = 0
    for bill in last:
        if (service_id == INTERNET) and bill.bill_tv_bill:
            ret += bill.bill_tv_bill
        if (service_id == PHONE) and bill.bill_phone_bill:
            ret += bill.bill_phone_bill
        if (service_id == HSC) and bill.bill_zhirovka:
            ret += bill.bill_zhirovka
    if (len(last) > 0):
        ret = round(ret / len(last), 2)
    return ret

def add_bill(user, apart):
    if (len(Task.objects.filter(user=user.id, app_apart=NUM_ROLE_METER, task_1=apart.id)) < 2):
        return None, _('there are no meter readings').capitalize()
    if not Task.objects.filter(user=user.id, app_apart=NUM_ROLE_BILL, task_1=apart.id).exists():
        # First bill
        prev = Task.objects.filter(user=user.id, app_apart=NUM_ROLE_METER, task_1=apart.id).order_by('start')[0]
        curr = Task.objects.filter(user=user.id, app_apart=NUM_ROLE_METER, task_1=apart.id).order_by('start')[1]
        period = curr.start
    else:
        last = Task.objects.filter(user=user.id, app_apart=NUM_ROLE_BILL, task_1=apart.id).order_by('-start')[0]
        period = next_period(last.start)
        if not Task.objects.filter(user=user.id, app_apart=NUM_ROLE_METER, task_1=apart.id, start=period).exists(): 
            return None, _('there are no meter readings for the next period').capitalize()
        prev = last.task_3
        curr = Task.objects.filter(user=user.id, app_apart=NUM_ROLE_METER, task_1=apart.id, start=period).get()

    internet = phone = zkx = 0
    if apart.apart_has_tv:
        internet = avg_accrual(user, apart, period, INTERNET)
    if apart.apart_has_phone:
        phone = avg_accrual(user, apart, period, PHONE)
    if apart.apart_has_zkx:
        zkx = avg_accrual(user, apart, period, HSC)
    task = Task.objects.create(user=user, app_apart=NUM_ROLE_BILL, task_1=apart, task_2=prev, task_3=curr, start=period, name=get_bill_name(period), event=datetime.now(), bill_tv_bill=internet, bill_phone_bill=phone, bill_zhirovka=zkx)
    return task, ''
