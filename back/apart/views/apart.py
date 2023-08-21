import os
from urllib.parse import urlparse, parse_qs
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from task.const import APP_APART, ROLE_APART, NUM_ROLE_METER, NUM_ROLE_PRICE, NUM_ROLE_BILL, NUM_ROLE_METER_PROP, NUM_ROLE_SERV_PROP
from apart.models import *
from core.views import BaseListView, BaseDetailView
from apart.forms.apart import CreateForm, EditForm
from apart.config import app_config
from apart.const import APART_METER, APART_SERVICE

app = APP_APART
role = ROLE_APART

class ListView(LoginRequiredMixin, PermissionRequiredMixin, BaseListView):
    model = Apart
    form_class = CreateForm
    permission_required = 'task.view_apart'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)


class DetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView):
    model = Apart
    form_class = EditForm
    permission_required = 'task.change_apart'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context(self.request.user.id))
        context['delete_question'] = _('delete apartment').capitalize()
        apart = self.object
        if ApartPrice.objects.filter(app_apart=NUM_ROLE_PRICE, task_1=apart.id).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because there are tariffs for this apartment').capitalize()
        elif PeriodMeters.objects.filter(app_apart=NUM_ROLE_METER, task_1=apart.id).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because there are meters data for this apartment').capitalize()
        elif PeriodServices.objects.filter(app_apart=NUM_ROLE_BILL, task_1=apart.id).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because there are bills for this apartment').capitalize()
        context['django_host_api'] = os.environ.get('DJANGO_HOST_API', 'http://localhost:8000')
        context['apart_id'] = apart.id
        context['meter_kinds'] = [{'code': k, 'name': v} for k, v in APART_METER.items()]
        context['apart_meters'] = ApartMeter.objects.filter(app_apart=NUM_ROLE_METER_PROP, task_1=apart.id).order_by('sort')
        context['service_kinds'] = [{'code': k, 'name': v[1]} for k, v in APART_SERVICE.items()]
        context['apart_services'] = ApartService.objects.filter(app_apart=NUM_ROLE_SERV_PROP, task_1=apart.id).order_by('sort')
        parts = urlparse(self.request.get_full_path())
        params = parse_qs(parts.query)
        context['active_tab'] = params.get('tab', 'meter')[0]
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.role_info()
        return response


