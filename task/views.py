from django.views.generic.edit import UpdateView
from django.utils.translation import gettext_lazy as _

from rusel.context import get_base_context
from rusel.utils import extract_get_params
from task.models import Group, TaskGroup
from task.forms import GroupForm

class GroupDetailView(UpdateView):
    model = Group
    template_name = 'base/group_detail.html'
    form_class = GroupForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        context.update(get_base_context(self.request, group.role, True, group.name))
        context['params'] = extract_get_params(self.request)
        context['ed_item'] = self.object
        if Group.objects.filter(node=self.object.id).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because there are subordinate groups').capitalize()
        else:
            if TaskGroup.objects.filter(group=self.object.id).exists():
                context['ban_on_deletion'] = _('deletion is prohibited because the group contains items').capitalize()
            else:
                context['ban_on_deletion'] = ''

        return context
