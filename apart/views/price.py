from datetime import date, datetime
from django.utils.translation import gettext_lazy as _
from task.const import ROLE_PRICE, NUM_ROLE_PRICE
from task.models import Task, TaskGroup, Urls, Step
from rusel.base.views import BaseDetailView, BaseGroupView, get_app_doc
from apart.views.base_list import BaseApartListView
from apart.forms.price import CreateForm, EditForm
from apart.models import Price, Apart
from apart.config import app_config

role = ROLE_PRICE

class TuneData:
    def tune_dataset(self, data, view_mode):
        return data

class ListView(BaseApartListView, TuneData):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def transform_datalist(self, items):
        apart = Apart.objects.filter(user=self.request.user, active=True).get()
        tasks = []
        for t in items.order_by('-name'):
            prc = Price.objects.filter(task=t.id).get()
            if (prc.apart.id != apart.id):
                continue
            item = {
                'id': t.id,
                'name': self.get_task_name(t),
                'attrs': self.get_info(t)
            }
            tasks.append(item)
        return tasks

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_PRICE
        response = super().form_valid(form)
        return response

    def get_task_name(self, task):
        prc = Price.objects.filter(task=task.id).get()
        return prc.start.strftime('%d.%m.%Y') + ' ' + prc.serv.name

    def get_info(self, item):
        ret = []
        prc = Price.objects.filter(task=item.id).get()
        b1 = prc.border
        if not b1:
            b1 = 0

        t1 = prc.tarif
        if not t1:
            t1 = 0

        b2 = prc.border2
        if not b2:
            b2 = 0

        t2 = prc.tarif2
        if not t2:
            t2 = 0

        t3 = prc.tarif3
        if not t3:
            t3 = 0

        p1 = ''
        p2 = ''
        p3 = ''

        if (b1 == 0):
            p1 = str(t1)
        else:
            p1 = '{:.3f} {} {:.0f} {}'.format(t1, _('until'), b1, prc.unit)
            if (b2 == 0):
                p2 = '{:.3f}'.format(t2)
            else:
                p2 = '{:.3f} {} {:.0f} {}'.format(t2, _('until'), b2, prc.unit)
                p3 = '{:.3f}'.format(t3)
    
        ret = []
        if p1:
            ret.append({'text': p1})
        if p2:
            ret.append({'icon': 'separator'})
            ret.append({'text': p2})
        if p3:
            ret.append({'icon': 'separator'})
            ret.append({'text': p3})
        return ret

class DetailView(BaseDetailView, TuneData):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)
