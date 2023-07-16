from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from task.const import APP_CRAM, ROLE_CRAM
from core.context import AppContext
from rusel.context import get_sorted_groups
from cram.models import CramGroup, Training
from cram.views.training import get_statist

class IndexView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'cram.view_phrase'
    template_name = 'cram/index.html'
    model = CramGroup
    fields = ['name']

    def get_context_data(self, **kwargs):
        app_context = AppContext(self.request.user, APP_CRAM, ROLE_CRAM)
        context = app_context.get_context()
        context['title'] = 'Заучивание'
        context['add_item_template'] = 'cram/add_item_input.html'
        groups = []
        get_sorted_groups(groups, self.request.user.id, ROLE_CRAM)
        context['groups'] = groups
        trainings = []
        sessions = Training.objects.filter(user=self.request.user.id).exclude(stop=None).exclude(ratio=0).order_by('-stop')
        for session in sessions:
            a = {
                'id': session.id,
                'date': session.stop,
                'ratio': session.ratio,
                'group': session.group.name,
                'data': get_statist(session),
            }
            trainings.append(a)
        context['trainings'] = trainings
        return context
    
    def post(self, request, *args, **kwargs):
        name = self.request.POST.get('add_item_name', '')
        if name:
            CramGroup.objects.create(user=self.request.user, name=name, act_items_qty=0)
        return super().post(request, *args, **kwargs)

