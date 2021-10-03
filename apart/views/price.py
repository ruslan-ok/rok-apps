from django.utils.translation import gettext_lazy as _
from task.const import ROLE_PRICE, NUM_ROLE_PRICE
from task.models import Task
from rusel.base.views import get_app_doc
from apart.views.base_list import BaseApartListView, BaseApartDetailView
from apart.forms.price import CreateForm, EditForm
from apart.models import Price
from apart.config import app_config

app = 'apart'
role = ROLE_PRICE

class ListView(BaseApartListView):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_PRICE
        response = super().form_valid(form)
        return response

class DetailView(BaseApartDetailView):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        if Price.objects.filter(task=form.instance.id).exists():
            price = Price.objects.filter(task=form.instance.id).get()
            price.start = form.cleaned_data['start']
            price.service = form.cleaned_data['service']
            price.tarif = form.cleaned_data['tarif']
            price.border = form.cleaned_data['border']
            price.tarif2 = form.cleaned_data['tarif2']
            price.border2 = form.cleaned_data['border2']
            price.tarif3 = form.cleaned_data['tarif3']
            price.save()
            form.instance.name = price.start.strftime('%d.%m.%Y') + ' ' + price.serv.name
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

    return {'attr': ret}

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)
