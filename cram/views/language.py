from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from task.const import APP_CRAM, ROLE_LANG
from cram.models import *
from cram.forms.language import CreateForm, EditForm
from cram.config import app_config
from cram.context import CramContext

app = APP_CRAM
role = ROLE_LANG

class LangListView(LoginRequiredMixin, PermissionRequiredMixin, ListView, CramContext):
    model = Lang
    form_class = CreateForm
    permission_required = 'cram.view_phrase'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(app_config, role)

    def get_context_data(self, **kwargs):
        if not self.request.user.is_authenticated:
            raise Http404
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context(self.request.user.id, None, icon=self.config.role_icon))
        context['title'] = _('Language list')
        return context

class LangDetailView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView, CramContext):
    model = Lang
    form_class = EditForm
    permission_required = 'cram.change_phrase'
    slug_field = 'code'
    slug_url_kwarg = 'lng'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(app_config, role)

    def get_context_data(self, **kwargs):
        if not self.request.user.is_authenticated:
            raise Http404
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context(self.request.user.id, None, icon=self.config.role_icon))
        context['title'] = _('Language form')
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.role_info()
        return response


