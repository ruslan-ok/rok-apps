import time, os

from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from django.http import FileResponse, HttpResponseNotFound

from rusel.context import get_cur_grp, get_base_context
from rusel.aside import Fix
from rusel.utils import extract_get_params, sort_data, get_search_mode
from task.const import *
from task.models import Task, Group, TaskGroup, Urls
#----------------------------
# Comment if MIGRATE
from todo.models import Todo
#----------------------------
from task.views import GroupDetailView
from task.forms import CreateGroupForm
from todo.const import *
from todo.forms import CreateTodoForm, TodoForm
from task.files import storage_path, get_files_list

list_url = '/todo/'

def get_tasks(user_id, mode, group_id):
    if (mode == MY_DAY):
        ret = Task.objects.filter(user=user_id, app_task=NUM_ROLE_TODO, in_my_day=True)
    elif (mode == IMPORTANT):
        ret = Task.objects.filter(user=user_id, app_task=NUM_ROLE_TODO, important=True).exclude(completed=True)
    elif (mode == PLANNED):
        ret = Task.objects.filter(user=user_id, app_task=NUM_ROLE_TODO).exclude(stop=None).exclude(completed=True)
    elif (mode == COMPLETED):
        ret = Task.objects.filter(user=user_id, app_task=NUM_ROLE_TODO, completed=True)
    elif (mode == BY_GROUP) and group_id:
        ret = []
        for tg in TaskGroup.objects.filter(group=group_id):
            if (tg.task.user.id == user_id) and (tg.task.app_task == NUM_ROLE_TODO):
                ret.append(tg.task)
    else: # ALL or NONE
        ret = Task.objects.filter(user=user_id, app_task=NUM_ROLE_TODO).exclude(completed=True)
    return ret

def get_filtered_tasks(user_id, mode, group_id, query):
    ret = get_tasks(user_id, mode, group_id)
    search_mode = get_search_mode(query)
    lookups = None
    if (search_mode == 0):
        return ret
    elif (search_mode == 1):
        lookups = Q(name__icontains=query) | Q(info__icontains=query) | Q(url__icontains=query)
    elif (search_mode == 2):
        lookups = Q(categories__icontains=query[1:])
    return ret.filter(lookups)

def sorted_tasks(user_id, mode, group_id, sort, sort_reverse, query):
    data = get_filtered_tasks(user_id, mode, group_id, query)
    return sort_data(data, sort + ' stop', sort_reverse)

class TodoAside():

    def get_aside_context(self, user):
        fixes = []
        list_url = reverse(app_name + ':todo-list')
        fixes.append(Fix('myday', _('my day').capitalize(), 'sun', list_url + '?view=myday', len(get_tasks(user, MY_DAY, 0).exclude(completed=True))))
        fixes.append(Fix('important', _('important').capitalize(), 'star', list_url + '?view=important', len(get_tasks(user, IMPORTANT, 0))))
        fixes.append(Fix('planned', _('planned').capitalize(), 'check2-square', list_url + '?view=planned', len(get_tasks(user, PLANNED, 0))))
        fixes.append(Fix('all', _('all').capitalize(), 'check-all', list_url, len(get_tasks(user, ALL, 0))))
        fixes.append(Fix('completed', _('completed').capitalize(), 'check2-circle', list_url + '?view=completed', len(get_tasks(user, COMPLETED, 0))))
        return fixes

    def get_fix_icon(self, mode):
        if (mode == MY_DAY):
            return 'sun'
        if (mode == IMPORTANT):
            return 'star'
        if (mode == PLANNED):
            return 'check2-square'
        if (mode == ALL):
            return 'check-all'
        if (mode == COMPLETED):
            return 'check2-circle'
        return 'check2-square'

class TodoListView(TodoAside, CreateView):
    #----------------------------
    # Comment if MIGRATE
    #model = Task
    model = Todo
    #----------------------------
    pagenate_by = 10
    template_name = 'base/list.html'
    title = _('unknown')
    view_as_tree = False
    form_class = CreateTodoForm

    def get_queryset(self):
        mode = ALL
        query = None
        if self.request.method == 'GET':
            mode = self.request.GET.get('view')
            query = self.request.GET.get('q')
        group = get_cur_grp(self.request)
        group_id = 0
        if group:
            group_id = group.id
        sort = 'created'
        sort_reverse = True
        return sorted_tasks(self.request.user.id, mode, group_id, sort, sort_reverse, query)

    def get_success_url(self):
        url = super().get_success_url()
        return url + extract_get_params(self.request)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.app_task = NUM_ROLE_TODO
        ret = super().form_valid(form)
        group_id = self.request.GET.get('group_id')
        if group_id:
            group = Group.objects.filter(id=group_id).get()
            TaskGroup.objects.create(task=form.instance, group=group, role=ROLE_TODO)
        return ret
    
    def get_context_data(self, **kwargs):
        mode = ALL
        query = None
        if self.request.method == 'GET':
            if ('view' in self.request.GET):
                mode = self.request.GET.get('view')
        context = super().get_context_data(**kwargs)
        title = _('all').capitalize()
        context.update(get_base_context(self.request, app_name, False, title))
        if (mode != BY_GROUP):
            context['title'] = _(PAGES[mode]).capitalize()
            context['content_icon'] = self.get_fix_icon(mode)
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
            items.append(Todo.from_Task(t, cur_grp))
        context['items'] = items
        #----------------------------
        return context
    
    def get_sorts(self):
        sorts = []
        return sorts

"""
================================================================
"""

class TodoDetailView(TodoAside, UpdateView):
    model = Task
    template_name = 'todo/todo_detail.html'
    title = _('unknown')
    form_class = TodoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.get_object()
        context.update(get_base_context(self.request, app_name, True, item.name))
        context['params'] = extract_get_params(self.request)
        context['fix_list'] = self.get_aside_context(self.request.user)
        context['ed_item'] = self.object
        context['urls'] = Urls.objects.filter(task=self.object.id).order_by('num')
        context['files'] = get_files_list(self.request.user, app_name, 'todo', item.id)

        return context

    def form_valid(self, form):
        grp = form.cleaned_data['grp']
        item = form.instance
        tg = None
        tgs = TaskGroup.objects.filter(task=item.id, role=ROLE_TODO)
        if (len(tgs) > 0):
            tg = tgs[0]
        if not tg and grp:
            TaskGroup.objects.create(task=item, group=grp, role=ROLE_TODO)
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
    return storage_path.format(user.id) + 'todo/todo_{}/'.format(item_id)

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


class TodoGroupDetailView(TodoAside, GroupDetailView):

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


