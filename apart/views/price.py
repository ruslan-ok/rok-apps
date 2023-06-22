from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from task.const import APP_APART, NUM_ROLE_APART, ROLE_PRICE, NUM_ROLE_PRICE
from apart.const import apart_service_name_by_id
from apart.models import Apart, ApartPrice
from rusel.base.views import BaseListView, BaseDetailView
from apart.forms.price import CreateForm, EditForm
from apart.config import app_config

app = APP_APART
role = ROLE_PRICE

class ListView(LoginRequiredMixin, PermissionRequiredMixin, BaseListView):
    model = ApartPrice
    form_class = CreateForm
    permission_required = 'task.view_apart'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_template_names(self):
        return ['apart/list.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_item_template'] = 'apart/add_price.html'
        cur_apart = None
        if Apart.objects.filter(user=self.request.user.id, app_apart=NUM_ROLE_APART, active=True).exists():
            cur_apart = Apart.objects.filter(user=self.request.user.id, app_apart=NUM_ROLE_APART, active=True).get()
        form = CreateForm(cur_apart)
        context['form'] = form
        return context

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_PRICE
        form.instance.set_name()
        response = super().form_valid(form)
        return response

class DetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView):
    model = ApartPrice
    form_class = EditForm
    permission_required = 'task.change_apart'

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['delete_question'] = _('delete tariff').capitalize()
        context['add_item_template'] = 'apart/add_price.html'
        context['service_name'] = apart_service_name_by_id(self.get_object().price_service)
        return context

    def form_valid(self, form):
        form.instance.set_name()
        response = super().form_valid(form)
        form.instance.save()
        form.instance.role_info()
        return response
