from django.utils.translation import gettext_lazy as _
from task.const import ROLE_BILL, NUM_ROLE_BILL
from task.models import Task
from rusel.base.views import get_app_doc
from apart.views.base_list import BaseApartListView, BaseApartDetailView
from apart.forms.bill import CreateForm, EditForm
from apart.config import app_config
from apart.models import Bill
from rusel.files import get_files_list

app = 'apart'
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
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if Bill.objects.filter(task=form.instance.id).exists():
            bill = Bill.objects.filter(task=form.instance.id).get()
            bill.period = form.cleaned_data['period']
            bill.save()
            form.instance.name = bill.period.strftime('%m.%Y')
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

    files = get_files_list(bill.apart.user, 'apart', 'bill', bill.id)

    if bill.url or bill.info or len(files):
        ret.append({'icon': 'separator'})

    if bill.url:
        ret.append({'icon': 'url'})

    if bill.info:
        ret.append({'icon': 'notes'})

    if len(files):
        ret.append({'icon': 'attach'})
    return {'attr': ret}

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)
