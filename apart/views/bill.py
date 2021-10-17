from datetime import datetime
from django.utils.translation import gettext_lazy as _
from task.const import APP_APART, ROLE_BILL, NUM_ROLE_BILL
from task.models import Task, Urls
from rusel.files import get_files_list
from rusel.base.views import get_app_doc
from apart.views.base_list import BaseApartListView, BaseApartDetailView
from apart.forms.bill import CreateForm, EditForm
from apart.config import app_config
from apart.models import Apart, Meter, Bill
from apart.views.meter import next_period
from rusel.files import get_files_list

app = APP_APART
role = ROLE_BILL

class ListView(BaseApartListView):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_BILL
        response = super().form_valid(form)
        return response

class DetailView(BaseApartDetailView):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        if Bill.objects.filter(task=self.get_object().id).exists():
            item = Bill.objects.filter(task=self.get_object().id).get()
            context['title'] = item.apart.name + ' ' + _('bill').capitalize() + ' ' + self.object.name
            context['ed_item'] = item
            vel = 0
            vga = 0
            vwt = 0

            if item.curr.el and item.prev.el:
                vel = item.curr.el - item.prev.el

            if item.curr.ga and item.prev.ga:
                vga = item.curr.ga - item.prev.ga

            if item.curr.hw and item.curr.cw and item.prev.hw and item.prev.cw:
                vwt = (item.curr.hw + item.curr.cw) - (item.prev.hw + item.prev.cw)

            context['volume'] = { 'el': vel, 'ga': vga, 'wt': vwt }
            context['el_tar'] = {'title': _('electricity').capitalize(), 'value': 777.88}
            context['el_bill'] = {'value': 777.88}
            context['gas_tar'] = {'title': _('gas').capitalize(), 'value': 777.88}
            context['gas_bill'] = {'value': 777.88}
            context['water_tar'] = {'title': _('water').capitalize(), 'value': 777.88}
            context['water_bill'] = {'value': 777.88}

            context['tv_title'] = _('Interet/TV')
            context['phone_title'] = _('phone').capitalize()
            context['ZKX_title'] = _('HCS')
            context['PoO_title'] = _('PoO')
            context['delete_question'] = _('delete bill').capitalize()
            context['ban_on_deletion'] = ''
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if Bill.objects.filter(task=form.instance.id).exists():
            bill = Bill.objects.filter(task=form.instance.id).get()
            bill.period = form.cleaned_data['period']
            bill.payment = form.cleaned_data['payment']
            bill.rate = form.cleaned_data['rate']
            bill.el_pay = form.cleaned_data['el_pay']
            bill.tv_bill = form.cleaned_data['tv_bill']
            bill.tv_pay = form.cleaned_data['tv_pay']
            bill.phone_bill = form.cleaned_data['phone_bill']
            bill.phone_pay = form.cleaned_data['phone_pay']
            bill.zhirovka = form.cleaned_data['zhirovka']
            bill.hot_pay = form.cleaned_data['hot_pay']
            bill.repair_pay = form.cleaned_data['repair_pay']
            bill.ZKX_pay = form.cleaned_data['ZKX_pay']
            bill.water_pay = form.cleaned_data['water_pay']
            bill.gas_pay = form.cleaned_data['gas_pay']
            bill.PoO = form.cleaned_data['PoO']
            bill.PoO_pay = form.cleaned_data['PoO_pay']
            bill.save()
            form.instance.name = bill.period.strftime('%Y.%m')
            form.instance.save()
        form.instance.set_item_attr(app, get_info(form.instance))
        return response

def get_info(item):
    if not Bill.objects.filter(task=item.id).exists():
        return {'attr': []}

    bill = Bill.objects.filter(task=item.id).get()
    ret = []
    ret.append({'text': '{}: {}'.format(_('total bill'), bill.total_bill()) })
    ret.append({'icon': 'separator'})
    ret.append({'text': '{}: {}'.format(_('total pay'), bill.total_pay()) })

    links = len(Urls.objects.filter(task=item.id)) > 0
    files = len(get_files_list(item.user, app, role, item.id)) > 0

    if item.info or links or files:
        ret.append({'icon': 'separator'})

    if item.info:
        ret.append({'icon': 'notes'})

    if links:
        ret.append({'icon': 'url'})

    if files:
        ret.append({'icon': 'attach'})
    return {'attr': ret}

def add_bill(request, task):
    apart = Apart.objects.filter(user=request.user.id, active=True).get()
    if (len(Meter.objects.filter(apart=apart.id)) < 2):
        # Нет показаний счетчиков
        return None, _('there are no meter readings').capitalize()

    if not Bill.objects.filter(apart=apart.id).exists():
        # Первая оплата
        prev = Meter.objects.filter(apart=apart.id).order_by('period')[0]
        curr = Meter.objects.filter(apart=apart.id).order_by('period')[1]
        period = curr.period
    else:
        last = Bill.objects.filter(apart=apart.id).order_by('-period')[0]
        period = next_period(last.period)
        if not Meter.objects.filter(apart=apart.id, period = period).exists(): 
            # Нет показаний счетчиков для очередного периода
            return None, _('there are no meter readings for the next period').capitalize()
        prev = last.curr
        curr = Meter.objects.filter(apart=apart.id, period = period).get()

    item = Bill.objects.create(apart=apart, period=period, task=task, payment=datetime.now(), prev=prev, curr=curr, rate=0)
    task.name = period.strftime('%Y.%m')
    task.set_item_attr(app, get_info(task))
    return item, ''

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)
