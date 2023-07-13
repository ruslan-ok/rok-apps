from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from core.context import AppContext
from cram.forms.group import GroupForm
from task.const import APP_CRAM, ROLE_CRAM
from task.models import Group
from cram.models import CramGroup, Phrase

class GroupView(LoginRequiredMixin, UpdateView):
    model = Group
    form_class = GroupForm
    permission_required = 'cram.view_phrase'
    template_name = 'cram/group.html'

    def get_success_url(self):
        group_id = int(self.kwargs.get('pk', '0'))
        if ('form_close' in self.request.POST):
            return reverse('cram:phrases', args=(group_id,))
        return reverse('cram:group', args=(group_id,))

    def get_context_data(self, **kwargs):
        app_context = AppContext(self.request.user, APP_CRAM, ROLE_CRAM)
        context = app_context.get_context()
        group = self.object
        context['config'] = {'app_title': 'Заучивание'}
        context['title'] = group.name
        context['add_item_template'] = 'core/add_item_input.html'
        context['delete_question'] = _('delete group').capitalize()
        if CramGroup.objects.filter(node=group.id).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because there are subordinate groups').capitalize()
        else:
            if Phrase.objects.filter(group=group.id).exists():
                context['ban_on_deletion'] = _('deletion is prohibited because the group contains items').capitalize()
            else:
                context['ban_on_deletion'] = ''
        context['add_item_placeholder'] = '{} {}'.format(_('create new').capitalize(), pgettext_lazy('create new ... ', 'group'))
        context['form'] = GroupForm(instance=group)
        return context
