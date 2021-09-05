import time
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView

from rusel.context import get_cur_grp, get_base_context
from rusel.aside import Fix
from rusel.utils import extract_get_params
from task.const import *
from task.models import Task, Group, TaskGroup
from task.views import GroupDetailView
from task.forms import CreateGroupForm
from note.const import *
from note.forms import CreateNoteForm, NoteForm

list_url = '/note/'

class NoteAside():

    def get_aside_context(self, user):
        fixes = []
        qty = len(Task.objects.filter(user=user.id, app_note=NOTE).exclude(completed=True))
        fixes.append(Fix('all', _('all').capitalize(), 'check-all', list_url, qty))
        return fixes


class NoteListView(NoteAside, CreateView):
    model = Task
    pagenate_by = 10
    template_name = 'base/list.html'
    view_id = ALL
    title = _('unknown')
    view_as_tree = False
    form_class = CreateNoteForm

    def get_queryset(self):
        cur_grp = get_cur_grp(self.request)
        if cur_grp:
            return [tg.task for tg in TaskGroup.objects.filter(group=cur_grp)]
        # ALL
        return Task.objects.filter(user=self.request.user, app_note=NOTE, completed=False).order_by('created')

    def get_success_url(self):
        url = super().get_success_url()
        return url + extract_get_params(self.request)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.app_note = NOTE
        ret = super().form_valid(form)
        l = self.request.GET.get('lst')
        if l:
            lst = Group.objects.filter(id=l).get()
            TaskGroup.objects.create(task=form.instance, group=lst, role=ROLE_NOTE)
        return ret
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = _('all').capitalize()
        context.update(get_base_context(self.request, app_name, False, title))
        context['fix_list'] = self.get_aside_context(self.request.user)
        context['group_form'] = CreateGroupForm()
        context['sort_options'] = self.get_sorts()
        context['view_id'] = self.view_id
        context['params'] = extract_get_params(self.request)
        context['item_detail_url'] = app_name + ':item-detail'
        context['content_icon'] = 'sticky'

        groups = []
        query = None
        page_number = 1
        if self.request.method == 'GET':
            query = self.request.GET.get('q')
            page_number = self.request.GET.get('page')
            if not page_number:
                page_number = 1
        search_mode = 0
    
        tasks = self.get_queryset()
        context['items'] = tasks
        return context
    
    def get_sorts(self):
        sorts = []
        return sorts

"""
================================================================
"""

class NoteDetailView(NoteAside, UpdateView):
    model = Task
    template_name = 'note/note_detail.html'
    title = _('unknown')
    form_class = NoteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.get_object()
        context.update(get_base_context(self.request, app_name, True, item.name))
        context['params'] = extract_get_params(self.request)
        context['fix_list'] = self.get_aside_context(self.request.user)
        context['ed_item'] = self.object
        return context

    def form_valid(self, form):
        grp = form.cleaned_data['grp']
        task = form.instance
        tg = None
        tgs = TaskGroup.objects.filter(task=task.id, role=ROLE_NOTE)
        if (len(tgs) > 0):
            tg = tgs[0]
        if not tg and grp:
            TaskGroup.objects.create(task=task, group=grp, role=ROLE_NOTE)
        else:
            if tg and not grp:
                tg.delete()
            else:
                if tg and grp:
                    tg.group = grp
                    tg.save()
        ret = super().form_valid(form)
        return ret

"""
================================================================
"""


class NoteGroupDetailView(NoteAside, GroupDetailView):

    def get_success_url(self):
        ret = ''
        if ('ret' in self.request.GET):
            ret = '?ret=' + self.request.GET['ret']
        url = reverse('note:group-detail', args=[self.get_object().id]) + ret
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        context['fix_list'] = self.get_aside_context(self.request.user)
        context['return_url'] = list_url
        return context


