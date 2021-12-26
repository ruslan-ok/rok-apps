from django.utils.translation import gettext_lazy as _
from task.const import APP_APART, ROLE_PRICE, NUM_ROLE_PRICE
from task.models import Task, Urls
from rusel.files import get_files_list, get_app_doc
from rusel.base.views import BaseListView, BaseDetailView
from apart.forms.price import CreateForm, EditForm
from apart.models import Apart, Price
from apart.config import app_config

app = APP_APART
role = ROLE_PRICE

class ListView(BaseListView):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def tune_dataset(self, data, group):
        return data

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_PRICE
        response = super().form_valid(form)
        return response

class DetailView(BaseDetailView):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def tune_dataset(self, data, group):
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Price.objects.filter(task=self.object.id).exists():
            item = Price.objects.filter(task=self.object.id).get()
            context['delete_question'] = _('delete tariff').capitalize()
            context['ban_on_deletion'] = ''
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if Price.objects.filter(task=form.instance.id).exists():
            item = Price.objects.filter(task=form.instance.id).get()
            item.start = form.cleaned_data['start']
            item.serv = form.cleaned_data['service']
            item.tarif = form.cleaned_data['tarif']
            item.border = form.cleaned_data['border']
            item.tarif2 = form.cleaned_data['tarif2']
            item.border2 = form.cleaned_data['border2']
            item.tarif3 = form.cleaned_data['tarif3']
            item.save()
            name = ''
            if item.serv:
                name = ' ' + item.serv.name
            form.instance.name = item.start.strftime('%Y.%m.%d') + name
            form.instance.save()
        form.instance.set_item_attr(app, get_info(form.instance))
        return response

def get_info(item):
    if not Price.objects.filter(task=item.id).exists():
        return {'attr': []}

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
        p1 = '{:.3f} {} {:.0f} {}'.format(t1, _('until'), b1, prc.unit if prc.unit else '')
        if (b2 == 0):
            p2 = '{:.3f}'.format(t2)
        else:
            p2 = '{:.3f} {} {:.0f} {}'.format(t2, _('until'), b2, prc.unit if prc.unit else '')
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

def add_price(request, task):
    apart = Apart.objects.filter(user=request.user.id, active=True).get()
    item = Price.objects.create(apart=apart, task=task)
    name = ''
    if item.serv:
        name = ' ' + item.serv.name
    task.name = item.start.strftime('%Y.%m.%d') + name
    task.start = item.start
    task.set_item_attr(app, get_info(task))
    return item

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)
