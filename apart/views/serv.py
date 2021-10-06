from django.utils.translation import gettext_lazy as _
from task.const import ROLE_SERVICE, NUM_ROLE_SERVICE
from task.models import Task
from rusel.files import get_files_list
from rusel.base.views import get_app_doc
from apart.forms.serv import CreateForm, EditForm
from apart.config import app_config
from apart.models import Service, Apart
from apart.views.base_list import BaseApartListView, BaseApartDetailView

app = 'apart'
role = ROLE_SERVICE

class ListView(BaseApartListView):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_SERVICE
        response = super().form_valid(form)
        apart = Apart.objects.filter(user=form.instance.user, active=True).get()
        Service.objects.create(apart=apart, task=form.instance, name=form.instance.name);
        return response

class DetailView(BaseApartDetailView):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Service.objects.filter(task=self.object.id).exists():
            item = Service.objects.filter(task=self.object.id).get()
            context['title'] = item.apart.name + ' ' + _('service').capitalize() + ' "' + self.object.name + '"'
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
    ret = [{'text': item.info}]
    files = (len(get_files_list(item.user, app, role, item.id)) > 0)
    if files:
        if item.info:
            ret.append({'icon': 'separator'})
        ret.append({'icon': 'attach'})
    return {'attr': ret}

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)
