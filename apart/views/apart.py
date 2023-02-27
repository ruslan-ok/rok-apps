from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from task.const import APP_APART, ROLE_APART, NUM_ROLE_SERVICE, NUM_ROLE_METER, NUM_ROLE_PRICE, NUM_ROLE_BILL
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView
from apart.forms.apart import CreateForm, EditForm
from apart.config import app_config

app = APP_APART
role = ROLE_APART

class ListView(LoginRequiredMixin, PermissionRequiredMixin, BaseListView):
    model = Task
    form_class = CreateForm
    permission_required = 'task.view_apart'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)


class DetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView):
    model = Task
    form_class = EditForm
    permission_required = 'task.change_apart'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

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
        get_info(form.instance)
        return response


def get_info(item):
    ret = []
    if item.apart_has_el or item.apart_has_hw or item.apart_has_cw or item.apart_has_gas or item.apart_has_tv or item.apart_has_phone or item.apart_has_zkx or item.apart_has_ppo:
        if item.apart_has_el:
            ret.append({'text': str(_('el'))})
        if item.apart_has_hw:
            ret.append({'text': str(_('hw'))})
        if item.apart_has_cw:
            ret.append({'text': str(_('cw'))})
        if item.apart_has_gas:
            ret.append({'text': str(_('gas'))})
        if item.apart_has_tv:
            ret.append({'text': str(_('inet/tv'))})
        if item.apart_has_phone:
            ret.append({'text': str(_('phone'))})
        if item.apart_has_zkx:
            ret.append({'text': str(_('zkx'))})
        if item.apart_has_ppo:
            ret.append({'text': str(_('ppo'))})
    item.actualize_role_info(app, role, ret)
