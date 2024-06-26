from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from task.const import APP_APART, ROLE_BILL, NUM_ROLE_BILL, NUM_ROLE_SERV_VALUE
from core.views import BaseListView, BaseDetailView
from apart.forms.bill import CreateForm, EditForm
from apart.calc_tarif import get_bill_meters
from apart.models import PeriodServices, ServiceAmount

app = APP_APART
role = ROLE_BILL

class ListView(LoginRequiredMixin, PermissionRequiredMixin, BaseListView):
    model = PeriodServices
    form_class = CreateForm
    permission_required = 'task.view_apart'

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    def get_queryset(self):
        data = super().get_queryset()
        query = None
        if (self.request.method == 'GET'):
            query = self.request.GET.get('q')
        if not data or query:
            return data
        return data[:12]

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_BILL
        response = super().form_valid(form)
        return response
    
class DetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView):
    model = PeriodServices
    form_class = EditForm
    permission_required = 'task.change_apart'

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        bill = self.get_object()
        context['delete_question'] = _('delete bill').capitalize()
        if PeriodServices.objects.filter(app_apart=NUM_ROLE_BILL, task_1=bill.task_1.id, start__gt=bill.start).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because it is not the last bill').capitalize()
        context['bill_meters'] = get_bill_meters(bill)
        context['bill_services'] = ServiceAmount.objects.filter(app_apart=NUM_ROLE_SERV_VALUE, task_1=self.object.task_1.id, start=self.object.start).order_by('sort')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        if 'start' in form.changed_data:
            old_start = form.initial['start']
            new_start = form.cleaned_data['start']
            services = ServiceAmount.objects.filter(app_apart=NUM_ROLE_SERV_VALUE, task_1=form.instance.task_1.id, start=old_start)
            for service in services:
                service.start = new_start
                service.save()
        form.instance.set_name()
        form.instance.role_info()
        return response

