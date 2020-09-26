import os, locale
from datetime import datetime, date, timedelta

from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from hier.utils import get_app_params, get_base_context_ext, process_common_commands, sort_data, extract_get_params
from hier.params import set_restriction, set_article_kind, set_article_visible, set_sort_mode, toggle_sort_dir, get_search_mode, get_search_info
from hier.categories import get_categories_list
from hier.grp_lst import group_add, group_details, group_toggle, list_add, list_details
from hier.files import File
from .models import app_name, Lst, Task, Param, Step, TaskFiles, DAILY, WORKDAYS, WEEKLY, MONTHLY, ANNUALLY, PerGrp
from .utils import get_task_status, nice_date, get_grp_planned, GRP_PLANNED_NONE, get_week_day_name
from .tree import build_tree
from .forms import TaskNameForm, TaskForm, StepForm, TaskFilesForm


NONE = ''
NAME = 'name'
CREATED = 'created'

ALL = 'all'
MY_DAY = 'myday'
IMPORTANT = 'important'
PLANNED = 'planned'
COMPLETED = 'completed'
LIST_MODE = 'list'

MODE_NAME = {
    NONE: _('all'),
    ALL: _('all'),
    MY_DAY: _('my day'),
    IMPORTANT: _('important'),
    PLANNED: _('planned'),
    COMPLETED: _('completed'),
    LIST_MODE: _('tasks of the list')
}


SORT_MODE_DESCR = {
    '': '',
    'important': _('sort by important'),
    'stop': _('sort by termin'),
    'in_my_day': _('sort by My day'),
    'name': _('sort by name'),
    'created': _('sort by create date')
}

TASK_DETAILS = 'task'
LIST_DETAILS = 'list'
GROUP_DETAILS = 'group'

def get_per_grp(user, grp_id):
    if PerGrp.objects.filter(user = user.id, grp_id = grp_id).exists():
        return PerGrp.objects.filter(user = user.id, grp_id = grp_id).get()
    return PerGrp.objects.create(user = user, grp_id = grp_id, is_open = True)

class Term():
    per_grp = None
    todo = []

    def __init__(self, user, grp_id):
        self.per_grp = get_per_grp(user, grp_id)
        self.todo = []

def get_tasks(user, mode, lst_id):
    if (mode == MY_DAY):
        ret = Task.objects.filter(user = user.id, in_my_day = True)
    elif (mode == IMPORTANT):
        ret = Task.objects.filter(user = user.id, important = True).exclude(completed = True)
    elif (mode == PLANNED):
        ret = Task.objects.filter(user = user.id).exclude(stop = None).exclude(completed = True)
    elif (mode == COMPLETED):
        ret = Task.objects.filter(user = user.id, completed = True)
    elif (mode == LIST_MODE):
        ret = Task.objects.filter(user = user.id, lst = lst_id)
    else: # ALL or NONE
        ret = Task.objects.filter(user = user.id).exclude(completed = True)
    return ret

def get_filtered_tasks(user, mode, lst_id, query):
    ret = get_tasks(user, mode, lst_id)
    search_mode = get_search_mode(query)
    lookups = None
    if (search_mode == 0):
        return ret
    elif (search_mode == 1):
        lookups = Q(name__icontains=query) | Q(info__icontains=query) | Q(url__icontains=query)
    elif (search_mode == 2):
        lookups = Q(categories__icontains=query[1:])
    return ret.filter(lookups)

def sorted_tasks(user, app_param, query):
    lst_id = 0
    if app_param.lst:
        lst_id = app_param.lst.id
    data = get_filtered_tasks(user, app_param.restriction, lst_id, query)
    return sort_data(data, app_param.sort + ' stop', app_param.reverse)

def todo_base_context(request):
    app_param = get_app_params(request.user, app_name)
    if (app_param.restriction == LIST_MODE) and app_param.lst:
        title = app_param.lst.name
    else:
        title = MODE_NAME[app_param.restriction].capitalize()
    app_param, context = get_base_context_ext(request, app_name, 'task', title)
    context['cur_view'] = app_param.restriction
    context['list_url'] = 'todo:' + app_param.restriction
    if app_param.lst:
        context['list_id'] = app_param.lst.id
    if (app_param.restriction == MY_DAY):
        context['list_info'] = datetime.today()
    context['in_my_day_qty'] = len(get_tasks(request.user, MY_DAY, 0).exclude(completed = True))
    context['important_qty'] = len(get_tasks(request.user, IMPORTANT, 0))
    context['planned_qty'] = len(get_tasks(request.user, PLANNED, 0))
    context['all_qty'] = len(get_tasks(request.user, ALL, 0))
    context['completed_qty'] = len(get_tasks(request.user, COMPLETED, 0))
    tree = build_tree(request.user.id, app_name)
    context['groups'] = tree
    if app_param.sort:
        context['sort_mode'] = SORT_MODE_DESCR[app_param.sort].capitalize()
    context['sort_dir'] = app_param.reverse
    return app_param, context

def get_remind_today():
    remind_today = datetime.now()
    remind_today += timedelta(hours = 3)
    if (remind_today.minute > 0):
        correct_min = -remind_today.minute
        if (remind_today.minute > 30):
            correct_min = 60 - remind_today.minute
        remind_today += timedelta(minutes = correct_min)
    return remind_today

def get_remind_tomorrow():
    return datetime.now().replace(hour = 9, minute = 0, second = 0) + timedelta(1)

def get_remind_next_week():
    return datetime.now().replace(hour = 9, minute = 0, second = 0) + timedelta(8 - datetime.today().isoweekday())

def complete_task(task):
    next = None
    if (not task.completed) and task.repeat:
        if not task.start:
            task.start = task.stop # Для повторяющейся задачи запоминаем срок, который был указан в первой итерации, чтобы использовать его для корректировки дат следующих этапов
        next = task.next_iteration()
    task.completed = not task.completed
    if task.completed:
        if not task.stop:
          task.stop = date.today()
        task.completion = datetime.now()
    else:
        task.completion = None
    task.save()
    if task.completed and next: # Завершен этап повторяющейся задачи и определен срок следующей итерации
        if not Task.objects.filter(user = task.user, name = task.name, lst = task.lst, completed = False).exists():
            Task.objects.create(user = task.user, lst = task.lst, name = task.name, start = task.start, stop = next, important = task.important, \
                                remind = task.next_remind_time(), repeat = task.repeat, repeat_num = task.repeat_num, \
                                repeat_days = task.repeat_days, categories = task.categories, info = task.info)

def get_task_details(request, context, pk, lst):
    ed_task = get_object_or_404(Task.objects.filter(id = pk, user = request.user.id))

    name_form = None
    form = None
    file_form = None

    if (request.method == 'POST'):
        #raise Exception(request.POST)
        if ('article_delete' in request.POST):
            ed_task.delete()
            set_article_visible(request.user, app_name, False)
            return True
        if ('category-delete' in request.POST):
            category = request.POST['category-delete']
            ed_task.categories = ed_task.categories.replace(category, '')
            ed_task.save()
            return True
        if ('task-name-save' in request.POST):
            name_form = TaskNameForm(request.POST, instance = ed_task)
            if name_form.is_valid():
                task = name_form.save(commit = False)
                task.user = request.user
                task.lst = lst
                name_form.save()
                return True
        if ('task-save' in request.POST):
            form = TaskForm(request.user, request.POST, instance = ed_task)
            if form.is_valid():
                task = form.save(commit = False)
                task.user = request.user
                if not request.POST['repeat']:
                    task.repeat = 0
                if form.cleaned_data['category']:
                    if task.categories:
                        task.categories += ' '
                    task.categories += form.cleaned_data['category']
                form.save()
                return True
        if ('task-file-upload' in request.POST):
            file_form = TaskFilesForm(request.POST, request.FILES)
            if file_form.is_valid():
                fl = file_form.save(commit = False)
                fl.user = request.user
                fl.task = ed_task
                fl.name = fl.upload.name
                fl.size = fl.upload.size
                f1, f2 = os.path.splitext(fl.name)
                fl.ext = f2[1:]
                file_form.save()
                return True
        if ('task-file-delete' in request.POST):
            tf = TaskFiles.objects.filter(user = request.user.id, id = int(request.POST['task-file-delete'])).get()
            tf.delete()
            return True
        if ('task-important' in request.POST):
            ed_task.important = not ed_task.important
            ed_task.save()
            return True
        if ('task-myday' in request.POST):
            ed_task.in_my_day = not ed_task.in_my_day
            ed_task.save()
            return True
        if ('task-completed' in request.POST):
            complete_task(ed_task)
            return True
        if ('step-add' in request.POST):
            task = Task.objects.filter(user = request.user, id = pk).get()
            step = Step.objects.create(name = request.POST['step_add_name'], task = task)
            return True
        if ('step-complete' in request.POST):
            step = Step.objects.filter(id = request.POST['step_id']).get()
            step.completed = not step.completed
            step.save()
            return True
        if ('step-save' in request.POST):
            step = Step.objects.filter(id = request.POST['step_id']).get()
            step.name = request.POST['step_edit_name']
            step.save()
            return True
        if ('step-delete' in request.POST):
            step = Step.objects.filter(id = request.POST['step_id']).get()
            step.delete()
            return True
        
        if ('remind-today' in request.POST):
            ed_task.remind = get_remind_today()
            ed_task.save()
            return True
        if ('remind-tomorrow' in request.POST):
            ed_task.remind = get_remind_tomorrow()
            ed_task.save()
            return True
        if ('remind-next-week' in request.POST):
            ed_task.remind = get_remind_next_week()
            ed_task.save()
            return True
        if ('remind-delete' in request.POST):
            ed_task.remind = None
            ed_task.save()
            return True
        
        if ('termin-today' in request.POST):
            ed_task.stop = datetime.today()
            ed_task.save()
            return True
        if ('termin-tomorrow' in request.POST):
            ed_task.stop = datetime.today() + timedelta(1)
            ed_task.save()
            return True
        if ('termin-next-week' in request.POST):
            ed_task.stop = datetime.today() + timedelta(8 - datetime.today().isoweekday())
            ed_task.save()
            return True
        if ('termin-delete' in request.POST):
            ed_task.stop = None
            if ed_task.repeat != 0:
                ed_task.repeat = 0
            ed_task.save()
            return True
        
        if ('repeat-daily' in request.POST):
            ed_task.repeat = DAILY
            ed_task.repeat_num = 1
            if not ed_task.stop:
                ed_task.stop = datetime.today()
            ed_task.save()
            return True
        if ('repeat-workdays' in request.POST):
            ed_task.repeat = WEEKLY
            ed_task.repeat_num = 1
            ed_task.repeat_days = 1+2+4+8+16
            if not ed_task.stop:
                ed_task.stop = datetime.today()
            ed_task.save()
            return True
        if ('repeat-weekly' in request.POST):
            ed_task.repeat = WEEKLY
            ed_task.repeat_num = 1
            ed_task.repeat_days = 0
            if not ed_task.stop:
                ed_task.stop = datetime.today()
            ed_task.save()
            return True
        if ('repeat-monthly' in request.POST):
            ed_task.repeat = MONTHLY
            ed_task.repeat_num = 1
            if not ed_task.stop:
                ed_task.stop = datetime.today()
            ed_task.save()
            return True
        if ('repeat-annually' in request.POST):
            ed_task.repeat = ANNUALLY
            ed_task.repeat_num = 1
            if not ed_task.stop:
                ed_task.stop = datetime.today()
            ed_task.save()
            return True
        if ('repeat-delete' in request.POST):
            ed_task.repeat = 0
            ed_task.save()
            return True
        if ('url-delete' in request.POST):
            ed_task.url = ''
            ed_task.save()
            return True

    if not name_form:
        name_form = TaskNameForm(instance = ed_task)

    if not form:
        form = TaskForm(request.user, instance = ed_task)

    if not file_form:
        file_form = TaskFilesForm()

    context['name_form'] = name_form
    context['form'] = form
    context['file_form'] = file_form
    context['files'] = get_files_list(request.user, ed_task.id)
    context['task_id'] = ed_task.id
    context['important'] = ed_task.important
    context['in_my_day'] = ed_task.in_my_day
    context['completed'] = ed_task.completed
    context['task_d_termin'] = ed_task.stop
    context['task_s_termin'] = ed_task.s_termin()
    context['task_actual'] = (not ed_task.completed) and (not ed_task.b_expired()) and ed_task.stop
    context['task_expired'] = ed_task.b_expired()
    
    context['steps'] = Step.objects.filter(task = ed_task.id)

    context['remind_active'] = ed_task.remind and (not ed_task.completed) and (ed_task.remind > datetime.now())
    context['task_b_remind'] = (ed_task.remind != None)
    if ed_task.remind:
        context['task_remind_time'] = _('remind in').capitalize() + ' ' + ed_task.remind.strftime('%H:%M')
        context['task_remind_date'] = nice_date(ed_task.remind.date())
    context['remind_today_info'] = get_remind_today().strftime('%H:%M')
    context['remind_tomorrow_info'] = get_remind_tomorrow().strftime('%a, %H:%M')
    context['remind_next_week_info'] = get_remind_next_week().strftime('%a, %H:%M')
    context['termin_today_info'] = datetime.today()
    context['termin_tomorrow_info'] = datetime.today() + timedelta(1)
    context['termin_next_week_info'] = datetime.today() + timedelta(8 - datetime.today().isoweekday())

    context['task_b_repeat'] = ed_task.repeat != 0
    context['task_s_repeat'] = ed_task.s_repeat()
    context['task_repeat_days'] = ed_task.repeat_s_days()

    context['repeat_form_d1'] = get_week_day_name(1)
    context['repeat_form_d2'] = get_week_day_name(2)
    context['repeat_form_d3'] = get_week_day_name(3)
    context['repeat_form_d4'] = get_week_day_name(4)
    context['repeat_form_d5'] = get_week_day_name(5)
    context['repeat_form_d6'] = get_week_day_name(6)
    context['repeat_form_d7'] = get_week_day_name(7)

    context['task_info'] = get_task_status(ed_task)
    context['categories'] = get_categories_list(ed_task.categories)
    context['url_cutted'] = ed_task.url
    if (len(ed_task.url) > 50):
        context['url_cutted'] = ed_task.url[:50] + '...'
    return False

def process_sort_commands(request):
    if ('sort-delete' in request.POST):
        set_sort_mode(request.user, app_name, '')
        return True
    if ('sort-important' in request.POST):
        set_sort_mode(request.user, app_name, 'important')
        return True
    if ('sort-termin' in request.POST):
        set_sort_mode(request.user, app_name, 'stop')
        return True
    if ('sort-myday' in request.POST):
        set_sort_mode(request.user, app_name, 'in_my_day')
        return True
    if ('sort-name' in request.POST):
        set_sort_mode(request.user, app_name, 'name')
        return True
    if ('sort-created' in request.POST):
        set_sort_mode(request.user, app_name, 'created')
        return True
    if ('sort-direction' in request.POST):
        toggle_sort_dir(request.user, app_name)
        return True
    return False


def get_files_list(user, task_id):
    ret = []
    npp = 1
    for f in TaskFiles.objects.filter(task = task_id):
        name = os.path.splitext(f.name)[0]
        ext = f.ext
        size = f.size
        url = f.upload.url
        fl = File(npp, name, ext, size, url)
        npp += 1
        ret.append(fl)
    return ret


def get_task_info(task, cur_view):
    ret = []
    
    if task.lst and (cur_view != LIST_MODE):
        ret.append({'text': task.lst.name})

    if task.in_my_day and (cur_view != MY_DAY):
        if (len(ret) > 0):
            ret.append({'icon': 'separator'})
        ret.append({'icon': 'myday', 'color': 'black', 'text': _('My day')})

    step_total = 0
    step_completed = 0
    for step in Step.objects.filter(task = task.id):
        step_total += 1
        if step.completed:
            step_completed += 1
    if (step_total > 0):
        if (len(ret) > 0):
            ret.append({'icon': 'separator'})
        ret.append({'text': '{} {} {}'.format(step_completed, _('out of'), step_total)})
    
    d = task.stop
    if d:
        if (len(ret) > 0):
            ret.append({'icon': 'separator'})
        s = task.s_termin()
        repeat = 'repeat'
        if task.b_expired():
            if task.completed:
                icon = 'termin'
                color = ''
            else:
                icon = 'termin-expired'
                color = 'expired'
                repeat = 'repeat-expired'
            ret.append({'icon': icon, 'color': color, 'text': s})
        elif (task.stop == date.today()):
            if task.completed:
                icon = 'termin'
                color = ''
            else:
                icon = 'termin-actual'
                color = 'actual'
                repeat = 'repeat-actual'
            ret.append({'icon': icon, 'color': color, 'text': s})
        else:
            ret.append({'icon': 'termin', 'text': s})

        if (task.repeat != 0):
            ret.append({'icon': repeat})


    if ((task.remind != None) and (task.remind >= datetime.now())) or task.info or (len(TaskFiles.objects.filter(task = task.id)) > 0):
        if (len(ret) > 0):
            ret.append({'icon': 'separator'})
        if ((task.remind != None) and (task.remind >= datetime.now())):
            ret.append({'icon': 'remind'})
        if task.info:
            ret.append({'icon': 'notes'})
        if (len(TaskFiles.objects.filter(task = task.id)) > 0):
            ret.append({'icon': 'attach'})

    if task.categories:
        if (len(ret) > 0):
            ret.append({'icon': 'separator'})
        categs = get_categories_list(task.categories)
        for categ in categs:
            ret.append({'icon': 'category', 'text': categ.name, 'color': 'category-design-' + categ.design})

    return ret

def find_term(data, user, grp_id):
    for term in data:
        if (term.per_grp.grp_id == grp_id):
            return term
    term = Term(user, grp_id)
    data.append(term)
    return term

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def task_list(request):
    locale.setlocale(locale.LC_CTYPE, request.LANGUAGE_CODE)
    locale.setlocale(locale.LC_TIME, request.LANGUAGE_CODE)

    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('todo:task_list') + extract_get_params(request))

    if process_sort_commands(request):
        return HttpResponseRedirect(reverse('todo:task_list') + extract_get_params(request))

    app_param, context = todo_base_context(request)

    if (request.method == 'POST'):
        if 'task-in-list-complete' in request.POST:
            task = Task.objects.filter(id = request.POST['task-in-list-complete']).get()
            complete_task(task)
            return HttpResponseRedirect(reverse('todo:task_list'))
        if 'task-in-list-important' in request.POST:
            task = Task.objects.filter(id = request.POST['task-in-list-important']).get()
            task.important = not task.important
            task.save()
            return HttpResponseRedirect(reverse('todo:task_list'))
        if 'task-add' in request.POST:
            lst = None
            if (app_param.restriction == 'list') and app_param.lst:
                lst = app_param.lst
            task = Task.objects.create(user = request.user, name = request.POST['task_add-name'], \
                                       lst = lst, in_my_day = (app_param.restriction == MY_DAY), important = (app_param.restriction == IMPORTANT))
            return HttpResponseRedirect(reverse('todo:task_form', args = [task.id]))
        if 'list-add' in request.POST:
            lst_id = list_add(request.user, app_name, request.POST['name'])
            return HttpResponseRedirect(reverse('todo:list_form', args = [lst_id]))
        if 'group-add' in request.POST:
            grp_id = group_add(request.user, app_name, request.POST['name'])
            return HttpResponseRedirect(reverse('todo:group_form', args = [grp_id]))

    template_file = ''
    redirect = False
    if app_param.article:
        if (app_param.kind == 'task'):
            if not Task.objects.filter(id = app_param.art_id, user = request.user.id).exists():
                set_article_visible(request.user, app_name, False)
                redirect = True
            else:
                template_file = 'todo/task_form.html'
                redirect = get_task_details(request, context, app_param.art_id, app_param.lst)
        elif (app_param.kind == 'list'):
            can_delete = not Task.objects.filter(lst = app_param.art_id).exists()
            redirect = list_details(request, context, app_param.art_id, app_name, can_delete)
            if not redirect:
                template_file = 'todo/list_form.html'
        elif (app_param.kind == 'group'):
            redirect = group_details(request, context, app_param.art_id, app_name)
            if not redirect:
                template_file = 'todo/group_form.html'

    if redirect:
        return HttpResponseRedirect(reverse('todo:task_list') + extract_get_params(request))

    if (template_file == ''):
        template_file = 'todo/task_list.html'
    
    context['details_pk'] = app_param.art_id

    data = []
    query = None
    if request.method == 'GET':
        query = request.GET.get('q')
    search_mode = 0
    for task in sorted_tasks(request.user, app_param, query):
        grp_id = get_grp_planned(app_param.restriction, task.stop, task.completed)
        term = find_term(data, request.user, grp_id)
        term.todo.append([task, get_task_info(task, app_param.restriction)])
    
    context['object_list'] = sorted(data, key=lambda term: term.per_grp.grp_id)
    context['search_info'] = get_search_info(query)
    context['task_add_form'] = TaskForm(request.user)

    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

def all_tasks(request):
    set_restriction(request.user, app_name, ALL)
    return HttpResponseRedirect(reverse('todo:task_list'))

def myday(request):
    set_restriction(request.user, app_name, MY_DAY)
    return HttpResponseRedirect(reverse('todo:task_list'))

def important(request):
    set_restriction(request.user, app_name, IMPORTANT)
    return HttpResponseRedirect(reverse('todo:task_list'))

def planned(request):
    set_restriction(request.user, app_name, PLANNED)
    return HttpResponseRedirect(reverse('todo:task_list'))

def completed(request):
    set_restriction(request.user, app_name, COMPLETED)
    return HttpResponseRedirect(reverse('todo:task_list'))

def list_items(request, pk):
    set_restriction(request.user, app_name, LIST_MODE, pk)
    return HttpResponseRedirect(reverse('todo:task_list'))

def task_form(request, pk):
    set_article_kind(request.user, app_name, TASK_DETAILS, pk)
    return HttpResponseRedirect(reverse('todo:task_list') + extract_get_params(request))

def list_form(request, pk):
    set_article_kind(request.user, app_name, LIST_DETAILS, pk)
    return HttpResponseRedirect(reverse('todo:task_list'))

def group_form(request, pk):
    set_article_kind(request.user, app_name, GROUP_DETAILS, pk)
    return HttpResponseRedirect(reverse('todo:task_list'))

def toggle_group(request, pk):
    group_toggle(request.user, app_name, pk)
    return HttpResponseRedirect(reverse('todo:task_list') + extract_get_params(request))

def period_toggle(request, pk):
    per_grp = get_object_or_404(PerGrp.objects.filter(user = request.user.id, grp_id = pk))
    per_grp.is_open = not per_grp.is_open
    per_grp.save()
    return HttpResponseRedirect(reverse('todo:task_list'))


