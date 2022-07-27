from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from task.const import APP_APART, ROLE_PRICE, NUM_ROLE_PRICE, APART_SERVICE
from task.models import Task, Urls
from rusel.base.views import BaseListView, BaseDetailView
from apart.forms.price import CreateForm, EditForm
from apart.config import app_config

app = APP_APART
role = ROLE_PRICE

class ListView(LoginRequiredMixin, BaseListView):
    model = Task
    form_class = CreateForm
    login_url = '/account/login/'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        self.template_name = 'apart/list.html'

    def tune_dataset(self, data, group):
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_item_template'] = 'apart/add_price.html'
        nav_item = Task.get_active_nav_item(self.request.user.id, APP_APART)
        form = CreateForm(nav_item)
        context['form'] = form
        return context

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_PRICE
        response = super().form_valid(form)
        return response

class DetailView(LoginRequiredMixin, BaseDetailView):
    model = Task
    form_class = EditForm
    login_url = '/account/login/'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def tune_dataset(self, data, group):
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_question'] = _('delete tariff').capitalize()
        context['add_item_template'] = 'apart/add_price.html'
        context['service_name'] = APART_SERVICE[self.get_object().price_service]
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.save()
        form.instance.name = get_price_name(form.instance.start, form.instance.price_service)
        form.instance.save()
        form.instance.set_item_attr(app, get_info(form.instance))
        return response

def get_info(item):
    b1 = item.price_border
    if not b1:
        b1 = 0

    t1 = item.price_tarif
    if not t1:
        t1 = 0

    b2 = item.price_border2
    if not b2:
        b2 = 0

    t2 = item.price_tarif2
    if not t2:
        t2 = 0

    t3 = item.price_tarif3
    if not t3:
        t3 = 0

    p1 = ''
    p2 = ''
    p3 = ''

    if (b1 == 0):
        p1 = str(t1)
    else:
        p1 = '{:.3f} {} {:.0f} {}'.format(t1, _('until'), b1, item.price_unit if item.price_unit else '')
        if (b2 == 0):
            p2 = '{:.3f}'.format(t2)
        else:
            p2 = '{:.3f} {} {:.0f} {}'.format(t2, _('until'), b2, item.price_unit if item.price_unit else '')
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
    files = (len(item.get_files_list(role)) > 0)
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

def get_price_name(start, service_id):
    return start.strftime('%Y.%m.%d') + ' ' + APART_SERVICE[service_id]

def add_price(user, apart, service_id):
    start = datetime.now()
    name = get_price_name(start, service_id)
    task = Task.objects.create(user=user, app_apart=NUM_ROLE_PRICE, task_1=apart, start=start, name=name, price_service=service_id)
    return task
