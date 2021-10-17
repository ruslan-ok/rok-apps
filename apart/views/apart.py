from django.utils.translation import gettext_lazy as _
from task.const import APP_APART, ROLE_APART, NUM_ROLE_APART
from task.models import Task
from rusel.files import get_files_list
from rusel.base.views import BaseListView, BaseDetailView, get_app_doc
from apart.forms.apart import CreateForm, EditForm
from apart.config import app_config
from apart.models import Apart

app = APP_APART
role = ROLE_APART

class ListView(BaseListView):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def tune_dataset(self, data, view_mode):
        return data

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_APART
        response = super().form_valid(form)
        Apart.objects.create(user=form.instance.user, task=form.instance, name=form.instance.name);
        return response


class DetailView(BaseDetailView):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def tune_dataset(self, data, view_mode):
        return data

    def form_valid(self, form):
        response = super().form_valid(form)
        if Apart.objects.filter(task=form.instance.id).exists():
            apart = Apart.objects.filter(task=form.instance.id).get()
            apart.has_el = form.cleaned_data['has_el']
            apart.has_hw = form.cleaned_data['has_hw']
            apart.has_cw = form.cleaned_data['has_cw']
            apart.has_gas = form.cleaned_data['has_gas']
            apart.has_tv = form.cleaned_data['has_tv']
            apart.has_phone = form.cleaned_data['has_phone']
            apart.has_zkx = form.cleaned_data['has_zkx']
            apart.has_ppo = form.cleaned_data['has_ppo']
            apart.save()
        form.instance.set_item_attr(app, get_info(form.instance))
        return response


def get_info(item):
    ret = {'attr': []}
    ret['attr'].append({'text': item.info})

    if Apart.objects.filter(task=item.id).exists():
        apart = Apart.objects.filter(task=item.id).get()
        files = (len(get_files_list(item.user, app, role, item.id)) > 0)
        if files:
            if item.info:
                ret['attr'].append({'icon': 'separator'})
            ret['attr'].append({'icon': 'attach'})
        if apart.has_el or apart.has_hw or apart.has_cw or apart.has_gas or apart.has_ppo:
            if item.info or files:
                ret['attr'].append({'icon': 'separator'})
            if apart.has_el:
                ret['attr'].append({'text': 'el'})
            if apart.has_hw:
                ret['attr'].append({'text': 'hw'})
            if apart.has_cw:
                ret['attr'].append({'text': 'cw'})
            if apart.has_gas:
                ret['attr'].append({'text': 'gas'})
            if apart.has_tv:
                ret['attr'].append({'text': 'inet/tv'})
            if apart.has_phone:
                ret['attr'].append({'text': 'phone'})
            if apart.has_zkx:
                ret['attr'].append({'text': 'zkx'})
            if apart.has_ppo:
                ret['attr'].append({'text': 'ppo'})

    return ret

def get_doc(request, pk, fname):
    return get_app_doc(app_config['name'], role, request, pk, fname)
