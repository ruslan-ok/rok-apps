import time, os

from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from django.http import FileResponse, HttpResponseNotFound

from rusel.context import get_cur_grp, get_base_context
from rusel.aside import Fix
from rusel.utils import extract_get_params
from task.const import *
from task.models import Task, Group, TaskGroup, Urls
#----------------------------
# Comment if MIGRATE
from note.models import Note
#----------------------------
from task.views import GroupDetailView
from task.forms import CreateGroupForm
from note.const import *
from note.forms import CreateNoteForm, NoteForm
from task.files import storage_path, get_files_list
from task.const import ROLE_NOTE

list_url = '/note/'

class NoteAside():

    def get_aside_context(self, user):
        fixes = []
        qty = len(Task.objects.filter(user=user.id, app_note=NUM_ROLE_NOTE).exclude(completed=True))
        fixes.append(Fix('all', _('all').capitalize(), 'check-all', list_url, qty))
        return fixes

class NoteListView(NoteAside, CreateView):
    #----------------------------
    # Comment if MIGRATE
    #model = Task
    model = Note
    #----------------------------
    pagenate_by = 10
    template_name = 'base/list.html'
    title = _('unknown')
    view_as_tree = False
    form_class = CreateNoteForm

    def get_queryset(self):
        cur_grp = get_cur_grp(self.request)
        if cur_grp:
            return [tg.task for tg in TaskGroup.objects.filter(group=cur_grp.id)]
        # ALL
        return Task.objects.filter(user=self.request.user, app_note=NUM_ROLE_NOTE, completed=False).order_by('created')

    def get_success_url(self):
        url = super().get_success_url()
        return url + extract_get_params(self.request)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.app_note = NUM_ROLE_NOTE
        ret = super().form_valid(form)
        group_id = self.request.GET.get('group_id')
        if group_id:
            group = Group.objects.filter(id=group_id).get()
            TaskGroup.objects.create(task=form.instance, group=group, role=ROLE_NOTE)
        return ret
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = _('all').capitalize()
        context.update(get_base_context(self.request, app_name, False, title))
        context['fix_list'] = self.get_aside_context(self.request.user)
        context['group_form'] = CreateGroupForm()
        context['sort_options'] = self.get_sorts()
        context['params'] = extract_get_params(self.request)
        context['item_detail_url'] = app_name + ':item-detail'
        context['hide_selector'] = True
        context['hide_important'] = True

        groups = []
        query = None
        page_number = 1
        if self.request.method == 'GET':
            query = self.request.GET.get('q')
            page_number = self.request.GET.get('page')
            if not page_number:
                page_number = 1
        search_mode = 0
    
        cur_grp = get_cur_grp(self.request)
        tasks = self.get_queryset()
        #context['items'] = tasks
        #----------------------------
        # Comment if MIGRATE
        items = []
        for t in tasks:
            items.append(Note.from_Task(t, cur_grp))
        context['items'] = items
        #----------------------------
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
        context['urls'] = Urls.objects.filter(task=self.object.id).order_by('num')
        context['files'] = get_files_list(self.request.user, app_name, ROLE_NOTE, item.id)

        return context

    def form_valid(self, form):
        grp = form.cleaned_data['grp']
        item = form.instance
        tg = None
        tgs = TaskGroup.objects.filter(task=item.id, role=ROLE_NOTE)
        if (len(tgs) > 0):
            tg = tgs[0]
        if not tg and grp:
            TaskGroup.objects.create(task=item, group=grp, role=ROLE_NOTE)
        else:
            if tg and not grp:
                tg.delete()
            else:
                if tg and grp:
                    tg.group = grp
                    tg.save()
        if ('url' in form.changed_data):
            url = form.cleaned_data['url']
            qty = len(Urls.objects.filter(task=item.id))
            Urls.objects.create(task=item, num=qty, href=url)
        if ('upload' in self.request.FILES):
            handle_uploaded_file(self.request.FILES['upload'], self.request.user, item.id)
        ret = super().form_valid(form)
        return ret

#----------------------------------
def get_file_storage_path(user, item_id):
    return storage_path.format(user.id) + app_name + '/note_{}/'.format(item_id)

#----------------------------------
def handle_uploaded_file(f, user, item_id):
    path = get_file_storage_path(user, item_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

#----------------------------------
def get_doc(request, pk, fname):
    path = get_file_storage_path(request.user, pk)
    try:
        fsock = open(path + fname, 'rb')
        return FileResponse(fsock)
    except IOError:
        response = HttpResponseNotFound()


"""
================================================================
"""


class NoteGroupDetailView(NoteAside, GroupDetailView):

    def get_success_url(self):
        ret = ''
        if ('ret' in self.request.GET):
            ret = '?ret=' + self.request.GET['ret']
        url = reverse(app_name + ':group-detail', args=[self.get_object().id]) + ret
        return url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = self.get_object()
        context['fix_list'] = self.get_aside_context(self.request.user)
        context['return_url'] = list_url
        return context


