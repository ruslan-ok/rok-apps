import os, locale
from datetime import datetime, date, timedelta

from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, HttpResponseNotFound
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from hier.utils import get_base_context_ext, process_common_commands, sort_data, extract_get_params
from hier.models import get_app_params, toggle_content_group
from hier.params import set_restriction, set_article_kind, set_article_visible, set_sort_mode, toggle_sort_dir, get_search_mode, get_search_info
from hier.categories import get_categories_list
from hier.grp_lst import group_add, group_details, group_toggle, list_add, list_details, build_tree
from hier.files import storage_path, get_files_list
from hier.aside import Fix, Sort
from hier.content import find_group
from .models import app_name, Lst, Task, Param, Step, DAILY, WORKDAYS, WEEKLY, MONTHLY, ANNUALLY#, PerGrp
from .utils import get_task_status, nice_date, get_grp_planned, GRP_PLANNED_NONE, get_week_day_name, GRPS_PLANNED
from .forms import TaskForm


items_in_page = 10

NONE = ''
NAME = 'name'
CREATED = 'created'

ALL = 'all'
MY_DAY = 'myday'
IMPORTANT = 'important'
PLANNED = 'planned'
COMPLETED = 'completed'
LIST_MODE = 'list'

PAGES = {
    NONE: 'all',
    ALL: 'all',
    MY_DAY: 'my day',
    IMPORTANT: 'important',
    PLANNED: 'planned',
    COMPLETED: 'completed',
    LIST_MODE: 'tasks of the list'
}


SORT_MODE_DESCR = {
    '': '',
    'important': _('sort by important'),
    'stop': _('sort by termin'),
    'completion': _('sort by completion date'),
    'in_my_day': _('sort by My day'),
    'name': _('sort by name'),
    'created': _('sort by create date')
}

TASK_DETAILS = 'task'
LIST_DETAILS = 'list'
GROUP_DETAILS = 'group'

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
    app_param, context = get_base_context_ext(request, app_name, 'task', (PAGES[app_param.restriction],))
    context['list_url'] = 'todo:' + app_param.restriction
    if (app_param.restriction == MY_DAY):
        context['title_info'] = datetime.today().strftime('%a, %d %B')

    fixes = []
    fixes.append(Fix('myday', _('my day').capitalize(), 'todo/icon/myday.png', 'myday/', len(get_tasks(request.user, MY_DAY, 0).exclude(completed = True))))
    fixes.append(Fix('important', _('important').capitalize(), 'todo/icon/important.png', 'important/', len(get_tasks(request.user, IMPORTANT, 0))))
    fixes.append(Fix('planned', _('planned').capitalize(), 'todo/icon/planned.png', 'planned/', len(get_tasks(request.user, PLANNED, 0))))
    fixes.append(Fix('all', _('all').capitalize(), 'rok/icon/all.png', 'all/', len(get_tasks(request.user, ALL, 0))))
    fixes.append(Fix('completed', _('completed').capitalize(), 'todo/icon/completed.png', 'completed/', len(get_tasks(request.user, COMPLETED, 0))))
    context['fix_list'] = fixes

    sorts = []
    if (app_param.restriction != MY_DAY):
        sorts.append(Sort('myday', _('my day').capitalize(), 'todo/icon/myday.png'))
    if (app_param.restriction != IMPORTANT):
        sorts.append(Sort('important', _('by importance').capitalize(), 'todo/icon/important.png'))
    sorts.append(Sort('termin', _('by termin date').capitalize(), 'todo/icon/planned.png'))
    if (app_param.restriction in (COMPLETED, LIST_MODE)):
        sorts.append(Sort('completion', _('by date of completion').capitalize(), 'todo/icon/completed.png'))
    sorts.append(Sort('name',  _('by name').capitalize(), 'todo/icon/sort.png'))
    sorts.append(Sort('created',  _('by creation date').capitalize(), 'todo/icon/created.png'))
    context['sort_options'] = sorts

    tree = build_tree(request.user.id, app_name)
    for t in tree:
        if t.is_list:
            t.qty = len(Task.objects.filter(user = request.user.id, lst = t.id, completed = False))
    context['groups'] = tree
    
    if app_param.sort and (app_param.sort in SORT_MODE_DESCR):
        context['sort_mode'] = SORT_MODE_DESCR[app_param.sort].capitalize()
    context['add_item_placeholder'] = _('add task').capitalize()
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

    form = None
    if (request.method == 'POST'):
        #raise Exception(request.POST)
        if ('item_delete' in request.POST):
            ed_task.delete()
            set_article_visible(request.user, app_name, False)
            return True
        if ('category_delete' in request.POST):
            category = request.POST['category_delete']
            ed_task.categories = ed_task.categories.replace(category, '')
            ed_task.save()
            return True
        if ('item_save' in request.POST):
            if request.POST['add_step']:
                task = Task.objects.filter(user = request.user, id = pk).get()
                step = Step.objects.create(name = request.POST['add_step'], task = task)
            form = TaskForm(request.user, request.POST, instance = ed_task)
            if form.is_valid():
                task = form.save(commit = False)
                task.user = request.user

                step_names = request.POST.getlist('step_edit_name')
                num = 0
                for x in request.POST.getlist('step_id'):
                     step = Step.objects.filter(id = x).get()
                     step.name = step_names[num]
                     step.save()
                     num += 1

                if not request.POST['repeat']:
                    task.repeat = 0
                if form.cleaned_data['category']:
                    if task.categories:
                        task.categories += ' '
                    task.categories += form.cleaned_data['category']
                form.save()
                return True
        if ('file_upload' in request.POST):
            form = TaskForm(request.user, request.POST, request.FILES)
            if form.is_valid():
                handle_uploaded_file(request.FILES['upload'], request.user, ed_task)
                return True
        if ('file_delete' in request.POST):
            delete_file(request.user, ed_task, request.POST['file_delete'])
            return True
        if ('task_important' in request.POST):
            ed_task.important = not ed_task.important
            ed_task.save()
            return True
        if ('task_myday' in request.POST):
            ed_task.in_my_day = not ed_task.in_my_day
            ed_task.save()
            return True
        if ('task_completed' in request.POST):
            complete_task(ed_task)
            return True
        if ('step_add' in request.POST):
            task = Task.objects.filter(user = request.user, id = pk).get()
            step = Step.objects.create(name = request.POST['add_step'], task = task)
            return True
        if ('step_complete' in request.POST):
            step = Step.objects.filter(id = request.POST['step_complete']).get()
            step.completed = not step.completed
            step.save()
            return True
        if ('step_delete' in request.POST):
            step = Step.objects.filter(id = request.POST['step_delete']).get()
            step.delete()
            return True
        
        if ('remind_today' in request.POST):
            ed_task.remind = get_remind_today()
            ed_task.save()
            return True
        if ('remind_tomorrow' in request.POST):
            ed_task.remind = get_remind_tomorrow()
            ed_task.save()
            return True
        if ('remind_next_week' in request.POST):
            ed_task.remind = get_remind_next_week()
            ed_task.save()
            return True
        if ('remind_delete' in request.POST):
            ed_task.remind = None
            ed_task.save()
            return True
        
        if ('termin_today' in request.POST):
            ed_task.stop = datetime.today()
            ed_task.save()
            return True
        if ('termin_tomorrow' in request.POST):
            ed_task.stop = datetime.today() + timedelta(1)
            ed_task.save()
            return True
        if ('termin_next_week' in request.POST):
            ed_task.stop = datetime.today() + timedelta(8 - datetime.today().isoweekday())
            ed_task.save()
            return True
        if ('termin_delete' in request.POST):
            ed_task.stop = None
            if ed_task.repeat != 0:
                ed_task.repeat = 0
            ed_task.save()
            return True
        
        if ('repeat_daily' in request.POST):
            ed_task.repeat = DAILY
            ed_task.repeat_num = 1
            if not ed_task.stop:
                ed_task.stop = datetime.today()
            ed_task.save()
            return True
        if ('repeat_workdays' in request.POST):
            ed_task.repeat = WEEKLY
            ed_task.repeat_num = 1
            ed_task.repeat_days = 1+2+4+8+16
            if not ed_task.stop:
                ed_task.stop = datetime.today()
            ed_task.save()
            return True
        if ('repeat_weekly' in request.POST):
            ed_task.repeat = WEEKLY
            ed_task.repeat_num = 1
            ed_task.repeat_days = 0
            if not ed_task.stop:
                ed_task.stop = datetime.today()
            ed_task.save()
            return True
        if ('repeat_monthly' in request.POST):
            ed_task.repeat = MONTHLY
            ed_task.repeat_num = 1
            if not ed_task.stop:
                ed_task.stop = datetime.today()
            ed_task.save()
            return True
        if ('repeat_annually' in request.POST):
            ed_task.repeat = ANNUALLY
            ed_task.repeat_num = 1
            if not ed_task.stop:
                ed_task.stop = datetime.today()
            ed_task.save()
            return True
        if ('repeat_delete' in request.POST):
            ed_task.repeat = 0
            ed_task.save()
            return True
        if ('url_delete' in request.POST):
            ed_task.url = ''
            ed_task.save()
            return True

    if not form:
        form = TaskForm(request.user, instance = ed_task)

    context['form'] = form
    context['files'] = get_files_list(request.user, app_name, 'task_{}'.format(ed_task.id))
    context['ed_item'] = ed_task
    context['task_actual'] = (not ed_task.completed) and (not ed_task.b_expired()) and ed_task.stop
    
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

    context['repeat_form_d1'] = get_week_day_name(1)
    context['repeat_form_d2'] = get_week_day_name(2)
    context['repeat_form_d3'] = get_week_day_name(3)
    context['repeat_form_d4'] = get_week_day_name(4)
    context['repeat_form_d5'] = get_week_day_name(5)
    context['repeat_form_d6'] = get_week_day_name(6)
    context['repeat_form_d7'] = get_week_day_name(7)

    context['item_info'] = get_task_status(ed_task)
    context['categories'] = get_categories_list(ed_task.categories)
    context['url_cutted'] = ed_task.url
    if (len(ed_task.url) > 50):
        context['url_cutted'] = ed_task.url[:50] + '...'
    return False

def process_sort_commands(request):
    if ('sort_delete' in request.POST):
        set_sort_mode(request.user, app_name, '')
        return True
    if ('sort_important' in request.POST):
        set_sort_mode(request.user, app_name, 'important')
        return True
    if ('sort_termin' in request.POST):
        set_sort_mode(request.user, app_name, 'stop')
        return True
    if ('sort_completion' in request.POST):
        set_sort_mode(request.user, app_name, 'completion')
        return True
    if ('sort_myday' in request.POST):
        set_sort_mode(request.user, app_name, 'in_my_day')
        return True
    if ('sort_name' in request.POST):
        set_sort_mode(request.user, app_name, 'name')
        return True
    if ('sort_created' in request.POST):
        set_sort_mode(request.user, app_name, 'created')
        return True
    if ('sort_direction' in request.POST):
        toggle_sort_dir(request.user, app_name)
        return True
    return False

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def task_list(request):
    # для трансляции строкового представления дат, в частности в item_info
    locale.setlocale(locale.LC_CTYPE, request.LANGUAGE_CODE)
    locale.setlocale(locale.LC_TIME, request.LANGUAGE_CODE)

    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('todo:task_list') + extract_get_params(request))

    if process_sort_commands(request):
        return HttpResponseRedirect(reverse('todo:task_list') + extract_get_params(request))

    app_param, context = todo_base_context(request)

    if (request.method == 'POST'):
        if 'item-in-list-select' in request.POST:
            task = Task.objects.filter(id = request.POST['item-in-list-select']).get()
            complete_task(task)
            return HttpResponseRedirect(reverse('todo:task_list') + extract_get_params(request))
        if 'item-in-list-important' in request.POST:
            task = Task.objects.filter(id = request.POST['item-in-list-important']).get()
            task.important = not task.important
            task.save()
            return HttpResponseRedirect(reverse('todo:task_list') + extract_get_params(request))
        if 'item-add' in request.POST:
            lst = None
            if (app_param.restriction == 'list') and app_param.lst:
                lst = app_param.lst
            task = Task.objects.create(user = request.user, name = request.POST['item_add-name'], \
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
                template_file = 'todo/task.html'
                redirect = get_task_details(request, context, app_param.art_id, app_param.lst)
        elif (app_param.kind == 'list'):
            can_delete = not Task.objects.filter(lst = app_param.art_id).exists()
            redirect = list_details(request, context, app_param.art_id, app_name, can_delete)
            if not redirect:
                template_file = 'hier/article_list.html'
        elif (app_param.kind == 'group'):
            redirect = group_details(request, context, app_param.art_id, app_name)
            if not redirect:
                template_file = 'hier/article_group.html'

    if redirect:
        return HttpResponseRedirect(reverse('todo:task_list') + extract_get_params(request))

    if (template_file == ''):
        template_file = 'todo/task.html'
    
    groups = []
    query = None
    if request.method == 'GET':
        query = request.GET.get('q')
    search_mode = 0

    tasks = sorted_tasks(request.user, app_param, query)
    for task in tasks:
        grp_id = get_grp_planned(app_param.restriction, task.stop, task.completed)
        group = find_group(groups, request.user, app_name, grp_id, GRPS_PLANNED[grp_id].capitalize())
        group.items.append(task)
    
    context['page_obj'] = tasks
    context['item_groups'] = sorted(groups, key = lambda group: group.grp.grp_id)
    context['search_info'] = get_search_info(query)
    context['search_qty'] = len(tasks)
    context['search_data'] = query and (len(tasks) > 0)
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
    toggle_content_group(request.user.id, app_name, pk)
    return HttpResponseRedirect(reverse('todo:task_list'))

def todo_entity(request, name, pk):
    if (name == 'task'):
        return task_form(request, pk)
    if (name == 'group'):
        return group_form(request, pk)
    if (name == 'list'):
        return list_form(request, pk)
    return task_list(request)

#----------------------------------
def get_file_storage_path(user, item):
    return storage_path.format(user.id) + 'todo/task_{}/'.format(item.id)

def handle_uploaded_file(f, user, item):
    path = get_file_storage_path(user, item)
    os.makedirs(os.path.dirname(path), exist_ok = True)
    with open(path + f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def task_get_doc(request, name):
    app_param = get_app_params(request.user, app_name)
    item = get_object_or_404(Task.objects.filter(id = app_param.art_id))
    path = get_file_storage_path(request.user, item)
    try:
        fsock = open(path + name, 'rb')
        return FileResponse(fsock)
    except IOError:
        response = HttpResponseNotFound()

def delete_file(user, item, name):
    path = get_file_storage_path(user, item)
    os.remove(path + name[4:])

#----------------------------------

