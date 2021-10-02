from datetime import date, datetime
from django.utils.translation import gettext_lazy as _
from task.const import ROLE_BILL, NUM_ROLE_BILL
from task.models import Task, TaskGroup, Urls, Step
from rusel.base.views import BaseDetailView, BaseGroupView, get_app_doc
from apart.views.base_list import BaseApartListView
from apart.forms.bill import CreateForm, EditForm
from apart.config import app_config
from apart.models import Bill, Apart
from rusel.files import get_files_list

role = ROLE_BILL

class TuneData:
    def tune_dataset(self, data, view_mode):
        return data

class ListView(BaseApartListView, TuneData):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
    """
    def transform_datalist(self, items):
        apart = Apart.objects.filter(user=self.request.user, active=True).get()
        tasks = []
        for t in items.order_by('-name'):
            bill = Bill.objects.filter(task=t.id).get()
            if (bill.apart.id != apart.id):
                continue
            item = {
                'id': t.id,
                'name': self.get_task_name(t),
                'attrs': self.get_info(t)
            }
            tasks.append(item)
        return tasks
    """

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_BILL
        response = super().form_valid(form)
        return response

    """
    def get_task_name(self, task):
        bill = Bill.objects.filter(task=task.id).get()
        return bill.period.strftime('%m.%Y')

    def get_info(self, item):
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
        return ret
    """

class DetailView(BaseDetailView, TuneData):
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

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)
