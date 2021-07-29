from django.views.generic.edit import UpdateView

from rusel.context import get_base_context
from rusel.utils import extract_get_params
from task.models import Group
from task.forms import GroupForm

class GroupDetailView(UpdateView):
    model = Group
    template_name = 'task/group_detail.html'
    form_class = GroupForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        context.update(get_base_context(self.request, group.app, True, group.name))
        context['params'] = extract_get_params(self.request)
        context['ed_item'] = self.object
        return context

