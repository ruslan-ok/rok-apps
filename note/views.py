import time
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView

from rusel.context import get_base_context
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
    cur_grp = 0

    def get_queryset(self):
        if (self.view_id == LIST_MODE):
            return [tg.task for tg in TaskGroup.objects.filter(group=self.cur_grp)]
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
            TaskGroup.objects.create(task=form.instance, group=lst, app=app_name)
        return ret
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.init_view()
        gp = self.get_group_path()
        context['group_path'] = gp
        title = _('all').capitalize()
        context.update(get_base_context(self.request, app_name, False, title))
        context['fix_list'] = self.get_aside_context(self.request.user)
        gf = CreateGroupForm()
        context['group_form'] = gf
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

    def init_view(self):
        self.view_id = ''
        self.cur_grp = 0
        if self.request.method == 'GET':
            v = self.request.GET.get('view')
            if v:
                self.view_id = v
            if (self.view_id == LIST_MODE):
                l = self.request.GET.get('lst')
                if l:
                    if Group.objects.filter(id=l, user=self.request.user.id).exists():
                        self.cur_grp = l
                if not self.cur_grp:
                    self.view_id = ALL
        
    def get_group_path(self):
        ret = []
        if (self.view_id == LIST_MODE) and self.cur_grp:
            grp = Group.objects.filter(id=self.cur_grp).get()
            ret.append({'id': grp.id, 'name': grp.name, 'edit_url': grp.edit_url})
            parent = grp.node
            while parent:
                grp = Group.objects.filter(id=parent.id).get()
                ret.append({'id': grp.id, 'name': grp.name, 'edit_url': grp.edit_url})
                parent = grp.node
        return ret
    
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


"""
================================================================
"""


class NoteGroupDetailView(NoteAside, GroupDetailView):

    def get_success_url(self):
        return reverse('note:group-detail', args=[self.get_object().id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        context['fix_list'] = self.get_aside_context(self.request.user)
        context['return_url'] = list_url
        return context


