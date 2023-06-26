from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from task.const import APP_APART, ROLE_METER, NUM_ROLE_METER, NUM_ROLE_BILL, NUM_ROLE_METER_VALUE
from core.views import BaseListView, BaseDetailView
from apart.forms.meter import CreateForm, EditForm
from apart.config import app_config
from apart.models import *

app = APP_APART
role = ROLE_METER

class ListView(LoginRequiredMixin, PermissionRequiredMixin, BaseListView):
    model = PeriodMeters
    form_class = CreateForm
    permission_required = 'task.view_apart'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_queryset(self):
        data = super().get_queryset()
        query = None
        if (self.request.method == 'GET'):
            query = self.request.GET.get('q')
        if not data or query:
            return data
        return data[:12]

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_METER
        response = super().form_valid(form)
        return response

class DetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView):
    model = PeriodMeters
    form_class = EditForm
    permission_required = 'task.change_apart'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_question'] = _('delete meters data').capitalize()
        if PeriodServices.objects.filter(app_apart=NUM_ROLE_BILL, task_2=self.object.id).exists() or PeriodServices.objects.filter(app_apart=NUM_ROLE_BILL, task_3=self.object.id).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because there are bills for this meters data').capitalize()
        if PeriodMeters.objects.filter(app_apart=NUM_ROLE_METER, task_1=self.object.task_1.id, start__gt=self.object.start).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because there is an entry with a higher date').capitalize()
        context['meter_value'] = MeterValue.objects.filter(app_apart=NUM_ROLE_METER_VALUE, task_1=self.object.task_1.id, start=self.object.start).order_by('sort')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.set_name()
        form.instance.role_info()
        return response
