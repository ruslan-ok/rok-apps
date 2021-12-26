from django.utils.translation import gettext_lazy as _
from task.const import APP_APART, ROLE_SERVICE, NUM_ROLE_SERVICE
from task.models import Task
from rusel.files import get_files_list, get_app_doc
from apart.forms.serv import CreateForm, EditForm
from apart.config import app_config
from apart.models import Service, Apart, Price
from rusel.base.views import BaseListView, BaseDetailView

app = APP_APART
role = ROLE_SERVICE

class ListView(BaseListView):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def tune_dataset(self, data, group):
        return data

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_SERVICE
        response = super().form_valid(form)
        apart = Apart.objects.filter(user=form.instance.user, active=True).get()
        Service.objects.create(apart=apart, task=form.instance, name=form.instance.name);
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
        if Service.objects.filter(task=self.object.id).exists():
            item = Service.objects.filter(task=self.object.id).get()
            context['delete_question'] = _('delete service').capitalize()
            context['ban_on_deletion'] = ''
            if Price.objects.filter(serv=item.id).exists():
                context['ban_on_deletion'] = _('deletion is prohibited because there are tariffs for this service').capitalize()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if Service.objects.filter(task=form.instance.id).exists():
            serv = Service.objects.filter(task=form.instance.id).get()
            serv.name = form.cleaned_data['name']
            serv.save()
        form.instance.set_item_attr(app, get_info(form.instance))
        return response

def get_info(item):
    ret = []
    files = (len(get_files_list(item.user, app, role, item.id)) > 0)
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
