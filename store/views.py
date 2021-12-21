from django.views.generic.edit import FormView
from django.urls import reverse
from django.http import HttpResponse
from django.template import loader
from task.const import ROLE_STORE, ROLE_APP
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView, Context, get_app_doc
from store.forms import CreateForm, EditForm, ParamsForm
from store.config import app_config
from store.get_info import get_info
from store.models import Entry, Params

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

class ListView(BaseListView, TuneData):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)


class DetailView(BaseDetailView, TuneData):
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
        this_entry = None
        if Entry.objects.filter(user=self.request.user.id, task=self.object.id, actual=1).exists():
            this_entry = Entry.objects.filter(user=self.request.user.id, task=self.object.id, actual=1)[0]
        else:
            if Entry.objects.filter(user=self.request.user.id, task=self.object.id).exists():
                this_entry = Entry.objects.filter(user=self.request.user.id, task=self.object.id)[0]
        if this_entry:
            hist = Entry.objects.filter(user=self.request.user, task=this_entry.task.id).exclude(id=this_entry.id)
            context['history'] = hist
            context['history_qty'] = len(hist)
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.set_item_attr(app, get_info(form.instance))
        form.instance.completed = not form.cleaned_data['actual']
        form.instance.save()
        if Entry.objects.filter(task=form.instance, hist=None).exists():
            entry = Entry.objects.filter(task=form.instance, hist=None)[0]
            entry.username = form.cleaned_data['username']
            entry.value = form.cleaned_data['value']
            entry.params = form.cleaned_data['params']
            entry.save()
        return response

class ParamsView(Context, TuneData):
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None
        self.request = request
        self.set_config(app_config, ROLE_STORE)
        self.config.set_view(request)

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
    context = params_view.get_app_context(icon=params_view.config.view_icon)
    context['form'] = form
    context['hide_add_item_input'] = True
    template = loader.get_template('store/params.html')
    return HttpResponse(template.render(context, request))

class GroupView(BaseGroupView, TuneData):
    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)

def get_store_params(user):
    if Params.objects.filter(user = user.id).exists():
        return Params.objects.filter(user = user.id).get()
    else:
        return Params.objects.create(user = user, ln = 30, uc = True, lc = True, dg = True, sp = True, br = True, mi = True, ul = True, ac = False)
