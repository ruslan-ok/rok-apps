from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from django.http import Http404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from cram.context import CramContext
from cram.config import app_config
from task.const import ROLE_CRAM

def training(request):
    return render(request, 'cram/training.html', context={})

class TrainingView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView, CramContext):
    template_name = "cram/training.html"
    permission_required = 'cram.view_phrase'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(app_config, ROLE_CRAM)

    def get_context_data(self, **kwargs):
        if not self.request.user.is_authenticated:
            raise Http404
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context(self.request.user.id, None, icon=self.config.role_icon))
        context['title'] = _('Cram training')
        context['hide_add_item_input'] = True
        return context

