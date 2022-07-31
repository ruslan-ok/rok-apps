from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template import loader
from task.const import ROLE_STORE, ROLE_APP, NUM_ROLE_STORE
from task.models import Task, Hist, PassParams
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView, Context
from store.forms import CreateForm, EditForm, ParamsForm
from store.config import app_config
from store.get_info import get_info

role = ROLE_STORE
app = ROLE_APP[role]

class TuneData:
    def tune_dataset(self, data, group):
        if (group.determinator == 'view'):
            if (group.view_id == 'actual'):
                return data.filter(completed=False)
            if (group.view_id == 'completed'):
                return data.filter(completed=True)
        return data

class ListView(LoginRequiredMixin, BaseListView, TuneData):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)


class DetailView(LoginRequiredMixin, BaseDetailView, TuneData):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        store_params = get_store_params(self.request.user)
        params = 0
        if store_params.uc:
            params += 1
        if store_params.lc:
            params += 2
        if store_params.dg:
            params += 4
        if store_params.sp:
            params += 8
        if store_params.br:
            params += 16
        if store_params.mi:
            params += 32
        if store_params.ul:
            params += 64
        if store_params.ac:
            params += 128
        context['default_len'] = store_params.ln
        context['default_params'] = params
        hist = Hist.objects.filter(task=self.get_object().id).order_by('-valid_until')
        context['store_history'] = hist
        context['store_history_qty'] = len(hist)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if (('store_username' in form.changed_data) or ('store_value' in form.changed_data)) and (
                (form.instance.store_username != form.initial['store_username']) or
                (form.instance.store_value != form.initial['store_value'])):
            Hist.objects.create(
                task=form.instance, 
                store_username=form.initial['store_username'],
                store_value=form.initial['store_value'],
                store_params=form.initial['store_params'],
                info=form.initial['info'],
                )
        form.instance.completed = not form.cleaned_data['actual']
        form.instance.save()
        form.instance.set_item_attr(app, get_info(form.instance))
        return response

class ParamsView(Context, TuneData):
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None
        self.request = request
        self.set_config(app_config, ROLE_STORE)
        self.config.set_view(request)

@login_required(login_url='account:login')
def params(request):
    form = None
    params = get_store_params(request.user)
    if (request.method == 'POST'):
        form = ParamsForm(request.POST, instance=params)
        if form.is_valid():
            data = form.save(commit = False)
            data.user = request.user
            form.save()
    if not form:
        form = ParamsForm(instance=params)
    
    params_view = ParamsView(request)
    context = params_view.get_app_context(request.user.id, icon=params_view.config.view_icon)
    context['form'] = form
    context['hide_add_item_input'] = True
    template = loader.get_template('store/params.html')
    return HttpResponse(template.render(context, request))

class GroupView(LoginRequiredMixin, BaseGroupView, TuneData):

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

def get_store_params(user):
    if PassParams.objects.filter(user = user.id).exists():
        return PassParams.objects.filter(user = user.id).get()
    else:
        return PassParams.objects.create(user = user, ln = 30, uc = True, lc = True, dg = True, sp = True, br = True, mi = True, ul = True, ac = False)

def add_item(user, name):
    params, username, value = PassParams.get_new_value(user)
    task = Task.objects.create(user=user, app_store=NUM_ROLE_STORE, name=name, event=datetime.now(), 
                                store_username=username, store_value=value, store_params=params)
    return task
