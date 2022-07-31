from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from task.const import APP_APART, ROLE_APART, NUM_ROLE_SERVICE, NUM_ROLE_METER, NUM_ROLE_PRICE, NUM_ROLE_BILL
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView
from apart.forms.apart import CreateForm, EditForm
from apart.config import app_config

app = APP_APART
role = ROLE_APART

class ListView(LoginRequiredMixin, BaseListView):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def tune_dataset(self, data, group):
        return data


class DetailView(LoginRequiredMixin, BaseDetailView):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def tune_dataset(self, data, group):
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context(self.request.user.id))
        #context['title'] = self.object.name
        context['delete_question'] = _('delete apartment').capitalize()
        if Task.objects.filter(app_apart=NUM_ROLE_SERVICE, task_1=self.object.id).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because there are services for this apartment').capitalize()
        elif Task.objects.filter(app_apart=NUM_ROLE_PRICE, task_1=self.object.id).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because there are tariffs for this apartment').capitalize()
        elif Task.objects.filter(app_apart=NUM_ROLE_METER, task_1=self.object.id).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because there are meters data for this apartment').capitalize()
        elif Task.objects.filter(app_apart=NUM_ROLE_BILL, task_1=self.object.id).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because there are bills for this apartment').capitalize()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.set_item_attr(app, get_info(form.instance))
        return response


def get_info(item):
    ret = {'attr': []}
    if item.info:
        info_descr = item.info[:80]
        if len(item.info) > 80:
            info_descr += '...'
        ret['attr'].append({'icon': 'notes', 'text': info_descr})

    files = (len(item.get_files_list(role)) > 0)
    if files:
        if item.info:
            ret['attr'].append({'icon': 'separator'})
        ret['attr'].append({'icon': 'attach'})
    if item.apart_has_el or item.apart_has_hw or item.apart_has_cw or item.apart_has_gas or item.apart_has_tv or item.apart_has_phone or item.apart_has_zkx or item.apart_has_ppo:
        if item.info or files:
            ret['attr'].append({'icon': 'separator'})
        if item.apart_has_el:
            ret['attr'].append({'text': str(_('el'))})
        if item.apart_has_hw:
            ret['attr'].append({'text': str(_('hw'))})
        if item.apart_has_cw:
            ret['attr'].append({'text': str(_('cw'))})
        if item.apart_has_gas:
            ret['attr'].append({'text': str(_('gas'))})
        if item.apart_has_tv:
            ret['attr'].append({'text': str(_('inet/tv'))})
        if item.apart_has_phone:
            ret['attr'].append({'text': str(_('phone'))})
        if item.apart_has_zkx:
            ret['attr'].append({'text': str(_('zkx'))})
        if item.apart_has_ppo:
            ret['attr'].append({'text': str(_('ppo'))})

    return ret
