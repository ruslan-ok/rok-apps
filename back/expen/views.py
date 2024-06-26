from django.utils.translation import gettext_lazy as _, pgettext_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.utils import formats
from task.const import ROLE_EXPENSE, ROLE_APP
from task.models import Task, TaskGroup
from core.views import BaseListView, BaseDetailView, BaseGroupView
from expen.forms import CreateForm, EditForm, ProjectForm
from expen.get_info import get_info

role = ROLE_EXPENSE
app = ROLE_APP[role]

class ListView(LoginRequiredMixin, PermissionRequiredMixin, BaseListView):
    model = Task
    form_class = CreateForm
    permission_required = 'task.view_expense'

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if (not self.config.cur_view_group.determinator):
            if ('group_path' in context):
                context['summary'] = self.config.cur_view_group.expen_summary()
        return context


class DetailView(LoginRequiredMixin, PermissionRequiredMixin, BaseDetailView):
    model = Task
    form_class = EditForm
    permission_required = 'task.change_expense'

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = context['title'] 
        if not title and self.object.expen_kontr:
            title = self.object.expen_kontr
        if not title and self.object.info:
            title = self.object.info.split('\n')[0]
        if not title and self.object.expen_qty and self.object.expen_price:
            title = str(self.object.expen_qty*self.object.expen_price)
        if not title:
            title = formats.date_format(self.object.event, 'd N Y')

        context['title'] = title
        context['summary'] = self.object.expen_item_summary()
        context['amount_curr'] = currency_repr(self.object.expen_amount())
        context['amount_usd'] = currency_repr(self.object.expen_amount('USD'))
        return context

    def get_group(self):
        tgs = TaskGroup.objects.filter(task=self.object.id, role=self.config.get_cur_role())
        if (len(tgs) > 0):
            return tgs[0].group
        return None

    def form_valid(self, form):
        response = super().form_valid(form)
        get_info(form.instance)
        return response

def currency_repr(value):
    if not value:
        return '0'
    if (round(value, 2) % 1):
        return '{:,.2f}'.format(value).replace(',', '`')
    return '{:,.0f}'.format(value).replace(',', '`')

class ProjectView(LoginRequiredMixin, BaseGroupView):
    form_class = ProjectForm
    template_name = 'expen/project.html'

    def __init__(self, *args, **kwargs):
        super().__init__(app, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['add_item_placeholder'] = '{} {}'.format(_('create new').capitalize(), pgettext_lazy('create new ... ', 'project'))
        return context
