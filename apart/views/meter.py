from datetime import date, datetime
from django.utils.translation import gettext_lazy as _
from task.const import APP_APART, ROLE_METER, NUM_ROLE_METER
from task.models import Task, Urls
from rusel.files import get_files_list
from rusel.base.views import get_app_doc, BaseGroupView
from apart.views.base_list import BaseApartListView, BaseApartDetailView
from apart.forms.meter import CreateForm, EditForm, ApartForm
from apart.config import app_config
from apart.models import Meter, Apart, Bill

app = APP_APART
role = ROLE_METER

class ListView(BaseApartListView):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_METER
        response = super().form_valid(form)
        return response

class DetailView(BaseApartDetailView):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Meter.objects.filter(task=self.object.id).exists():
            item = Meter.objects.filter(task=self.object.id).get()
            context['title'] = item.apart.name + ' ' + _('meters data').capitalize() + ' ' + self.object.name
            context['delete_question'] = _('delete meters data').capitalize()
            context['ban_on_deletion'] = ''
            if Bill.objects.filter(prev=item.id).exists() or Bill.objects.filter(curr=item.id).exists():
                context['ban_on_deletion'] = _('deletion is prohibited because there are bills for this meters data').capitalize()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if Meter.objects.filter(task=form.instance.id).exists():
            meter = Meter.objects.filter(task=form.instance.id).get()
            meter.period = form.cleaned_data['period']
            meter.reading = form.cleaned_data['reading']
            meter.el = form.cleaned_data['el']
            meter.hw = form.cleaned_data['hw']
            meter.cw = form.cleaned_data['cw']
            meter.ga = form.cleaned_data['ga']
            meter.save()
            form.instance.name = meter.period.strftime('%Y.%m')
            form.instance.save()
        form.instance.set_item_attr(app, get_info(form.instance))
        return response

def get_info(item):
    if not Meter.objects.filter(task=item.id).exists():
        return {'attr': []}

    ret = []
    meter = Meter.objects.filter(task=item.id).get()
    if (meter.apart.has_el):
        ret.append({'text': '{} {}'.format(_('el:'), meter.el)})
    if (meter.apart.has_hw):
        if ret:
            ret.append({'icon': 'separator'})
        ret.append({'text': '{} {}'.format(_('hw:'), meter.hw)})
    if (meter.apart.has_cw):
        if ret:
            ret.append({'icon': 'separator'})
        ret.append({'text': '{} {}'.format(_('cw:'), meter.cw)})
    if (meter.apart.has_gas):
        if ret:
            ret.append({'icon': 'separator'})
        ret.append({'text': '{} {}'.format(_('ga:'), meter.ga)})
    links = len(Urls.objects.filter(task=item.id)) > 0
    files = (len(get_files_list(item.user, app, role, item.id)) > 0)
    if item.info or links or files:
        if ret:
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

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)

#----------------------------------
def next_period(last = None):
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

def add_meter(request, task):
    apart = Apart.objects.filter(user=request.user.id, active=True).get()
    few = Meter.objects.filter(apart=apart.id).order_by('-period')[:3]
    qty = len(few)
    if (qty == 0):
        period = next_period()
        el = 0
        hw = 0
        cw = 0
        ga = 0
    else:
        last = few[0]
        period = next_period(last.period)

        el = last.el
        hw = last.hw
        cw = last.cw
        ga = last.ga

        if (qty > 1):
            first = few[qty-1]
            el = last.el + round((last.el - first.el) / (qty - 1))
            hw = last.hw + round((last.hw - first.hw) / (qty - 1))
            cw = last.cw + round((last.cw - first.cw) / (qty - 1))
            if last.ga:
                ga = last.ga + round((last.ga - first.ga) / (qty - 1))

    item = Meter.objects.create(apart=apart, period=period, task=task, reading=datetime.now(), el=el, hw=hw, cw=cw, ga=ga)
    task.event = item.reading
    task.name = item.period.strftime('%Y.%m')
    task.start = item.period
    task.set_item_attr(app, get_info(task))
    return item


class ApartView(BaseGroupView):
    form_class = ApartForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)
