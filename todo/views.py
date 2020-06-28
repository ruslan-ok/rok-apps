import os
from datetime import datetime, date, timedelta

from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from hier.utils import get_base_context, process_common_commands, set_aside_visible, set_article_visible
from .models import Grp, Lst, Task, Param, Step, TaskFiles
from .utils import TERM_NAME, ALL, get_task_status
from .tree import build_tree
from .forms import GrpForm, LstForm, TaskForm, TaskLstForm, TaskInfoForm, StepForm, TaskFilesForm

# Modes
ALL = 0
MY_DAY = 1
IMPORTANT = 2
PLANNED = 3
COMPLETED = 4
LIST_MODE = 7


NONE = 0
NAME = 5
CREATED = 6

MODE_ID = {
    ALL: 'all',
    MY_DAY: 'myday',
    IMPORTANT: 'important',
    PLANNED: 'planned',
    COMPLETED: 'completed',
    LIST_MODE: 'list_list'
}

MODE_NAME = {
    ALL: _('all'),
    MY_DAY: _('my day'),
    IMPORTANT: _('important'),
    PLANNED: _('planned'),
    COMPLETED: _('completed'),
    LIST_MODE: _('tasks of the list')
}


SORT_MODE_DESCR = {
    NONE: '',
    IMPORTANT: _('sort by important'),
    PLANNED: _('sort by termin'),
    MY_DAY: _('sort by My day'),
    NAME: _('sort by name'),
    CREATED: _('sort by create date')
}

TASK_DETAILS = 1
LIST_DETAILS = 2
GROUP_DETAILS = 3


class Term():
    id = 0
    name = ''
    is_open = False
    todo = []

    def __init__(self, id, name, is_open):
        self.id = id
        self.name = name
        self.is_open = is_open
        self.todo = []

def get_param(user):
    if Param.objects.filter(user = user.id).exists():
        return Param.objects.filter(user = user.id).get()
    return Param.objects.create(user = user, cur_view = ALL,
                                all_sort_mode = NONE, all_sort_dir = False,
                                myday_sort_mode = NONE, myday_sort_dir = False,
                                important_sort_mode = NONE, important_sort_dir = False,
                                planned_sort_mode = NONE, planned_sort_dir = False,
                                completed_sort_mode = NONE, completed_sort_dir = False)

def get_sort_mode(user, mode):
    param = get_param(user)
    if (mode == ALL):
        return param.all_sort_mode, param.all_sort_dir
    if (mode == MY_DAY):
        return param.myday_sort_mode, param.myday_sort_dir
    if (mode == IMPORTANT):
        return param.important_sort_mode, param.important_sort_dir
    if (mode == PLANNED):
        return param.planned_sort_mode, param.planned_sort_dir
    if (mode == COMPLETED):
        return param.completed_sort_mode, param.completed_sort_dir
    if (mode == LIST_MODE):
        return param.list_sort_mode, param.list_sort_dir
    return NONE, False

def set_sort_mode(user, sort_mode):
    param = get_param(user)
    if (param.cur_view == ALL):
        param.all_sort_mode = sort_mode
    if (param.cur_view == MY_DAY):
        param.myday_sort_mode = sort_mode
    if (param.cur_view == IMPORTANT):
        param.important_sort_mode = sort_mode
    if (param.cur_view == PLANNED):
        param.planned_sort_mode = sort_mode
    if (param.cur_view == COMPLETED):
        param.completed_sort_mode = sort_mode
    if (param.cur_view == LIST_MODE):
        param.list_sort_mode = sort_mode
    param.save()

def toggle_sort_dir(user):
    param = get_param(user)
    if (param.cur_view == ALL):
        param.all_sort_dir = not param.all_sort_dir
    if (param.cur_view == MY_DAY):
        param.myday_sort_dir = not param.myday_sort_dir
    if (param.cur_view == IMPORTANT):
        param.important_sort_dir = not param.important_sort_dir
    if (param.cur_view == PLANNED):
        param.planned_sort_dir = not param.planned_sort_dir
    if (param.cur_view == COMPLETED):
        param.completed_sort_dir = not param.completed_sort_dir
    if (param.cur_view == LIST_MODE):
        param.list_sort_dir = not param.list_sort_dir
    param.save()

def get_tasks(user, mode, lst_id):
    ret = []
    if (mode == ALL):
        ret = Task.objects.filter(user = user.id).exclude(completed = True)
    if (mode == MY_DAY):
        ret = Task.objects.filter(user = user.id, in_my_day = True)
    if (mode == IMPORTANT):
        ret = Task.objects.filter(user = user.id, important = True).exclude(completed = True)
    if (mode == PLANNED):
        ret = Task.objects.filter(user = user.id).exclude(start = None).exclude(completed = True)
    if (mode == COMPLETED):
        ret = Task.objects.filter(user = user.id, completed = True)
    if (mode == LIST_MODE):
        ret = Task.objects.filter(user = user.id, lst = lst_id)
    return ret

def sorted_tasks(user, mode, lst_id):
    sort_mode, sort_dir = get_sort_mode(user, mode)
    data = get_tasks(user, mode, lst_id)

    if (sort_mode == IMPORTANT) and (not sort_dir):
        data = data.order_by('important', '-start')
    elif (sort_mode == IMPORTANT) and sort_dir:
        data = data.order_by('-important', '-start')
    elif (sort_mode == PLANNED) and (not sort_dir):
        data = data.order_by('-start')
    elif (sort_mode == PLANNED) and sort_dir:
        data = data.order_by('start')
    elif (sort_mode == MY_DAY) and (not sort_dir):
        data = data.order_by('-in_my_day', '-start')
    elif (sort_mode == MY_DAY) and sort_dir:
        data = data.order_by('in_my_day', '-start')
    elif (sort_mode == NAME) and (not sort_dir):
        data = data.order_by('name', '-start')
    elif (sort_mode == NAME) and sort_dir:
        data = data.order_by('-name', '-start')
    elif (sort_mode == CREATED) and (not sort_dir):
        data = data.order_by('created', '-start')
    elif (sort_mode == CREATED) and sort_dir:
        data = data.order_by('-created', '-start')

    return data

def todo_base_context(request, mode, lst):
    context = get_base_context(request, 0, 0, _('tasks'), 'content_list', make_tree = False)
    context['cur_view'] = MODE_ID[mode]
    context['list_url'] = 'todo:' + MODE_ID[mode]
    if (mode == LIST_MODE) and lst:
        title = lst.name
    else:
        title = MODE_NAME[mode].capitalize()
    if lst:
        context['list_id'] = lst.id
    context['list_title'] = title
    if (mode == MY_DAY):
        context['list_info'] = datetime.today()
    context['title'] = title + ' - To Do'
    context['in_my_day_qty'] = len(get_tasks(request.user, MY_DAY, 0))
    context['important_qty'] = len(get_tasks(request.user, IMPORTANT, 0))
    context['planned_qty'] = len(get_tasks(request.user, PLANNED, 0))
    context['all_qty'] = len(get_tasks(request.user, ALL, 0))
    context['completed_qty'] = len(get_tasks(request.user, COMPLETED, 0))
    tree = build_tree(request.user.id)
    context['groups'] = tree
    sort_mode, sort_dir = get_sort_mode(request.user, mode)
    if sort_mode:
        context['sort_mode'] = SORT_MODE_DESCR[sort_mode].capitalize()
    context['sort_dir'] = sort_dir
    context['termin_today_info'] = 'пн'
    context['termin_tomorrow_info'] = 'пн'
    context['termin_next_week_info'] = 'пн'
    return context


def get_task_details(request, context, pk, lst):
    ed_task = get_object_or_404(Task.objects.filter(id = pk, user = request.user.id))
    form = None
    form_lst = None
    form_info = None
    form_file = None
    if (request.method == 'POST'):
        if 'task-save' in request.POST:
            form = TaskForm(request.POST, instance = ed_task, prefix = 'task_edit')
            if form.is_valid():
                task = form.save(commit = False)
                task.user = request.user
                task.lst = lst
                task.last_mod = datetime.now()
                form.save()
                return True
        if 'task-lst-save' in request.POST:
            form_lst = TaskLstForm(request.POST, instance = ed_task, prefix = 'task_lst_edit')
            if form_lst.is_valid():
                task = form_lst.save(commit = False)
                task.user = request.user
                task.last_mod = datetime.now()
                form_lst.save()
                return True
        if 'task-info-save' in request.POST:
            form_info = TaskInfoForm(request.POST, instance = ed_task, prefix = 'task_info_edit')
            if form_info.is_valid():
                task = form_info.save(commit = False)
                task.user = request.user
                task.last_mod = datetime.now()
                form_info.save()
                return True
        if 'task-file-upload' in request.POST:
            form_file = TaskFilesForm(request.POST, request.FILES)
            if form_file.is_valid():
                fl = form_file.save(commit = False)
                fl.user = request.user
                fl.task = ed_task
                fl.name = fl.upload.name
                fl.size = fl.upload.size
                f1, f2 = os.path.splitext(fl.name)
                fl.ext = f2[1:]
                form_file.save()
                return True
        if 'task-file-delete' in request.POST:
            tf = TaskFiles.objects.filter(user = request.user.id, id = int(request.POST['task-file-delete'])).get()
            tf.delete()
            return True
        if 'task-important' in request.POST:
            ed_task.important = not ed_task.important
            ed_task.save()
            return True
        if 'task-myday' in request.POST:
            ed_task.in_my_day = not ed_task.in_my_day
            ed_task.save()
            return True
        if 'task-completed' in request.POST:
            ed_task.completed = not ed_task.completed
            if ed_task.completed:
                ed_task.stop = date.today()
            ed_task.save()
            return True
        if 'task-delete' in request.POST:
            ed_task.delete()
            set_details(request.user, NONE, 0)
            return True
        if ('step-add' in request.POST):
            task = Task.objects.filter(user = request.user, id = pk).get()
            step = Step.objects.create(name = request.POST['step_add-name'], created = datetime.now(), last_mod = datetime.now(), task = task)
            return True
        if ('step-complete' in request.POST):
            step = Step.objects.filter(id = request.POST['step_edit_id']).get()
            step.completed = not step.completed
            step.save()
            return True
        if ('step-save' in request.POST):
            step = Step.objects.filter(id = request.POST['step_edit_id']).get()
            step.name = request.POST['step_edit_name']
            step.save()
            return True
        if ('step-delete' in request.POST):
            step = Step.objects.filter(id = request.POST['step_edit_id']).get()
            step.delete()
            return True

    if not form:
        form = TaskForm(instance = ed_task, prefix = 'task_edit')

    if not form_lst:
        form_lst = TaskLstForm(instance = ed_task, prefix = 'task_lst_edit')

    if not form_info:
        form_info = TaskInfoForm(instance = ed_task, prefix = 'task_info_edit')

    if not form_file:
        form_file = TaskFilesForm()

    context['form'] = form
    context['form_lst'] = form_lst
    context['form_info'] = form_info
    context['files'] = TaskFiles.objects.filter(task = ed_task.id)
    context['form_file'] = form_file
    context['task_id'] = ed_task.id
    context['created'] = ed_task.created
    context['important'] = ed_task.important
    context['in_my_day'] = ed_task.in_my_day
    context['completed'] = ed_task.completed
    context['task_status'] = get_task_status(ed_task)
    context['task_start'] = ed_task.start
    context['task_term'] = ed_task.term
    context['task_expired'] = ed_task.expired
    context['steps'] = Step.objects.filter(task = ed_task.id)
    context['step_form'] = StepForm(prefix = 'step_form')
    return False


def get_list_details(request, context, pk):
    ed_lst = get_object_or_404(Lst.objects.filter(id = pk, user = request.user.id))
    form = None
    if (request.method == 'POST'):
        if 'list-save' in request.POST:
            form = LstForm(request.POST, instance = ed_lst, prefix = 'lst_edit')
            if form.is_valid():
                lst = form.save(commit = False)
                lst.user = request.user
                lst.last_mod = datetime.now()
                form.save()
                return True
        elif 'list-delete' in request.POST:
            ed_lst.delete()
            set_details(request.user, NONE, 0)
            return True

    if not form:
        form = LstForm(instance = ed_lst, prefix = 'lst_edit')

    context['lst_form'] = form
    return False

def get_group_details(request, context, pk):
    ed_grp = get_object_or_404(Grp.objects.filter(id = pk, user = request.user.id))
    form = None
    if (request.method == 'POST'):
        if 'group-save' in request.POST:
            form = GrpForm(request.user, request.POST, instance = ed_grp, prefix = 'grp_edit')
            if form.is_valid():
                grp = form.save(commit = False)
                grp.user = request.user
                grp.last_mod = datetime.now()
                form.save()
                return True
        elif 'group-delete' in request.POST:
            ed_grp.delete()
            set_details(request.user, NONE, 0)
            return True

    if not form:
        form = GrpForm(request.user, instance = ed_grp, prefix = 'grp_edit')

    context['grp_form'] = form
    return False

def process_sort_commands(request):
    if ('sort-delete' in request.POST):
        set_sort_mode(request.user, NONE)
        return True
    if ('sort-important' in request.POST):
        set_sort_mode(request.user, IMPORTANT)
        return True
    if ('sort-termin' in request.POST):
        set_sort_mode(request.user, PLANNED)
        return True
    if ('sort-myday' in request.POST):
        set_sort_mode(request.user, MY_DAY)
        return True
    if ('sort-name' in request.POST):
        set_sort_mode(request.user, NAME)
        return True
    if ('sort-created' in request.POST):
        set_sort_mode(request.user, CREATED)
        return True
    if ('sort-direction' in request.POST):
        toggle_sort_dir(request.user)
        return True
    return False

def task_list(request):
    if process_common_commands(request):
        return HttpResponseRedirect(reverse('todo:task_list'))

    if process_sort_commands(request):
        return HttpResponseRedirect(reverse('todo:task_list'))

    param = get_param(request.user)

    if (request.method == 'POST'):
        if 'article_delete' in request.POST:
            article_delete(request)
            return HttpResponseRedirect(reverse('todo:task_list'))
        if 'task-in-list-complete' in request.POST:
            task = Task.objects.filter(id = request.POST['task-in-list-complete']).get()
            task.completed = not task.completed
            if task.completed:
                task.stop = date.today()
            task.save()
            return HttpResponseRedirect(reverse('todo:task_list'))
        if 'task-in-list-important' in request.POST:
            task = Task.objects.filter(id = request.POST['task-in-list-important']).get()
            task.important = not task.important
            task.save()
            return HttpResponseRedirect(reverse('todo:task_list'))
        if 'task-add' in request.POST:
            task = Task.objects.create(user = request.user, name = request.POST['task_add-name'], created = datetime.now(), \
                                       last_mod = datetime.now(), lst = param.lst, in_my_day = (param.cur_view == MY_DAY), important = (param.cur_view == IMPORTANT))
            return HttpResponseRedirect(reverse('todo:task_form', args = [task.id]))
        if 'list-add' in request.POST:
            lst = Lst.objects.create(user = request.user, name = request.POST['name'], created = datetime.now(), last_mod = datetime.now())
            return HttpResponseRedirect(reverse('todo:list_form', args = [lst.id]))
        if 'group-add' in request.POST:
            grp = Grp.objects.create(user = request.user, name = request.POST['name'], created = datetime.now(), last_mod = datetime.now())
            return HttpResponseRedirect(reverse('todo:group_form', args = [grp.id]))

    context = todo_base_context(request, param.cur_view, param.lst)

    details_mode = ''
    redirect = ''
    if (param.details_mode == TASK_DETAILS):
        details_mode = 'task'
        redirect = get_task_details(request, context, param.details_pk, param.lst)
    elif (param.details_mode == LIST_DETAILS):
        details_mode = 'list'
        redirect = get_list_details(request, context, param.details_pk)
    elif (param.details_mode == GROUP_DETAILS):
        details_mode = 'group'
        redirect = get_group_details(request, context, param.details_pk)

    if redirect:
        return HttpResponseRedirect(reverse('todo:task_list'))

    context['details_mode'] = details_mode
    context['details_pk'] = param.details_pk

    data = []
    terms = []
    if (param.cur_view != PLANNED):
        t = Term(ALL, TERM_NAME[ALL].capitalize(), True)
        data.append(t)

    for task in sorted_tasks(request.user, param.cur_view, param.lst):
        if (param.cur_view == PLANNED):
            term = task.count_term()
            terms.append(term)
            t = find_term(data, term)
        t.todo.append(task)
    
    context['object_list'] = data
    context['task_add_form'] = TaskForm(prefix='task_add')

    template_file = 'todo/task_list.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

def set_view(user, view, lst_id = 0):
    param = get_param(user)
    param.cur_view = view
    lst = None
    if lst_id:
        lst = Lst.objects.filter(user = user.id, id = lst_id).get()
    param.lst = lst
    param.save()
    set_aside_visible(user, False)

def all_tasks(request):
    set_view(request.user, ALL)
    return HttpResponseRedirect(reverse('todo:task_list'))

def myday(request):
    set_view(request.user, MY_DAY)
    return HttpResponseRedirect(reverse('todo:task_list'))

def important(request):
    set_view(request.user, IMPORTANT)
    return HttpResponseRedirect(reverse('todo:task_list'))

def planned(request):
    set_view(request.user, PLANNED)
    return HttpResponseRedirect(reverse('todo:task_list'))

def completed(request):
    set_view(request.user, COMPLETED)
    return HttpResponseRedirect(reverse('todo:task_list'))

def list_items(request, pk):
    set_view(request.user, LIST_MODE, pk)
    return HttpResponseRedirect(reverse('todo:task_list'))

def set_details(user, details_mode, pk):
    param = get_param(user)
    param.details_mode = details_mode
    param.details_pk = pk
    param.save()
    set_article_visible(user, param.details_mode in (TASK_DETAILS, LIST_DETAILS, GROUP_DETAILS))

def task_form(request, pk):
    set_details(request.user, TASK_DETAILS, pk)
    return HttpResponseRedirect(reverse('todo:task_list'))

def list_form(request, pk):
    set_view(request.user, LIST_MODE, pk)
    set_details(request.user, LIST_DETAILS, pk)
    return HttpResponseRedirect(reverse('todo:task_list'))

def group_form(request, pk):
    set_details(request.user, GROUP_DETAILS, pk)
    return HttpResponseRedirect(reverse('todo:task_list'))

def group_toggle(request, pk):
    grp = get_object_or_404(Grp.objects.filter(user = request.user.id, id = pk))
    grp.is_open = not grp.is_open
    grp.save()
    return HttpResponseRedirect(reverse('todo:task_list'))

def article_delete(request):
    param = get_param(request.user)
    if (param.details_mode == TASK_DETAILS):
        data = get_object_or_404(Task.objects.filter(user = request.user.id, id = param.details_pk))
        data.delete()
        set_details(request.user, NONE, 0)
    elif (param.details_mode == LIST_DETAILS):
        if not Task.objects.filter(lst = param.details_pk).exists():
            data = get_object_or_404(Lst.objects.filter(user = request.user.id, id = param.details_pk))
            data.delete()
            set_details(request.user, NONE, 0)
    elif (param.details_mode == GROUP_DETAILS):
        if not Grp.objects.filter(node = param.details_pk).exists() and not Lst.objects.filter(grp = param.details_pk).exists():
            data = get_object_or_404(Grp.objects.filter(user = request.user.id, id = param.details_pk))
            data.delete()
            set_details(request.user, NONE, 0)

