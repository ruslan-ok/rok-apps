import os, locale, pytz
from datetime import datetime, date, timedelta

from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hier.utils import get_base_context, process_common_commands, set_aside_visible, set_article_visible
from .models import Grp, Lst, Task, Param, Step, TaskFiles, NONE, DAILY, WORKDAYS, WEEKLY, MONTHLY, ANNUALLY, PerGrp
from .utils import get_task_status, nice_date, get_grp_planned, GRP_PLANNED_NONE, get_week_day_name
from .tree import build_tree
from .forms import GrpForm, LstForm, TaskForm, TaskLstForm, TaskInfoForm, StepForm, TaskFilesForm, TaskRemindForm, TaskTerminForm, TaskRepeatForm

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
        ret = Task.objects.filter(user = user.id).exclude(stop = None).exclude(completed = True)
    if (mode == COMPLETED):
        ret = Task.objects.filter(user = user.id, completed = True)
    if (mode == LIST_MODE):
        ret = Task.objects.filter(user = user.id, lst = lst_id)
    return ret

def sorted_tasks(user, mode, lst_id):
    sort_mode, sort_dir = get_sort_mode(user, mode)
    data = get_tasks(user, mode, lst_id)

    if (sort_mode == IMPORTANT) and (not sort_dir):
        data = data.order_by('important', '-stop')
    elif (sort_mode == IMPORTANT) and sort_dir:
        data = data.order_by('-important', '-stop')
    elif (sort_mode == PLANNED) and (not sort_dir):
        data = data.order_by('-completion', '-stop')
    elif (sort_mode == PLANNED) and sort_dir:
        data = data.order_by('completion', 'stop')
    elif (sort_mode == MY_DAY) and (not sort_dir):
        data = data.order_by('-in_my_day', '-stop')
    elif (sort_mode == MY_DAY) and sort_dir:
        data = data.order_by('in_my_day', '-stop')
    elif (sort_mode == NAME) and (not sort_dir):
        data = data.order_by('name', '-stop')
    elif (sort_mode == NAME) and sort_dir:
        data = data.order_by('-name', '-stop')
    elif (sort_mode == CREATED) and (not sort_dir):
        data = data.order_by('created', '-stop')
    elif (sort_mode == CREATED) and sort_dir:
        data = data.order_by('-created', '-stop')

    return data

def todo_base_context(request, mode, lst):
    context = get_base_context(request, 0, 0, _('tasks'), 'content_list', make_tree = False, article_enabled = True)
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
    context['termin_today_info'] = datetime.today()
    context['termin_tomorrow_info'] = datetime.today() + timedelta(1)
    context['termin_next_week_info'] = datetime.today() + timedelta(8 - datetime.today().isoweekday())
    return context


def get_remind_today(user_tz):
    remind_today = timezone.now().astimezone(user_tz)
    remind_today += timedelta(hours = 3)
    if (remind_today.minute > 0):
        correct_min = -remind_today.minute
        if (remind_today.minute > 30):
            correct_min = 60 - remind_today.minute
        remind_today += timedelta(minutes = correct_min)
    return remind_today

def get_remind_tomorrow(user_tz):
    today = timezone.now()
    return user_tz.localize(datetime(today.year, today.month, today.day, 9, 0, 0) + timedelta(1))

def get_remind_next_week(user_tz):
    return datetime(date.today().year, date.today().month, date.today().day, 9, 0, 0) + timedelta(8 - datetime.today().isoweekday())

def get_task_details(request, context, pk, lst, user_tz):
    ed_task = get_object_or_404(Task.objects.filter(id = pk, user = request.user.id))
    form = None
    form_lst = None
    form_info = None
    form_file = None
    form_remind = None
    form_termin = None
    form_repeat = None
    if (request.method == 'POST'):
        if ('task-save' in request.POST):
            form = TaskForm(request.POST, instance = ed_task, prefix = 'task_edit')
            if form.is_valid():
                task = form.save(commit = False)
                task.user = request.user
                task.lst = lst
                form.save()
                return True
        if ('task-lst-save' in request.POST):
            form_lst = TaskLstForm(request.POST, instance = ed_task, prefix = 'task_lst_edit')
            if form_lst.is_valid():
                task = form_lst.save(commit = False)
                task.user = request.user
                form_lst.save()
                return True
        if ('task-info-save' in request.POST):
            form_info = TaskInfoForm(request.POST, instance = ed_task, prefix = 'task_info_edit')
            if form_info.is_valid():
                task = form_info.save(commit = False)
                task.user = request.user
                form_info.save()
                return True
        if ('task-file-upload' in request.POST):
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
            ed_task.completed = not ed_task.completed
            if ed_task.completed:
                if not ed_task.stop:
                    ed_task.stop = date.today()
                ed_task.completion = timezone.now()
            else:
                ed_task.completion = None
            ed_task.save()
            return True
        if ('task-delete' in request.POST):
            ed_task.delete()
            set_details(request.user, NONE, 0)
            return True

        if ('step-add' in request.POST):
            task = Task.objects.filter(user = request.user, id = pk).get()
            step = Step.objects.create(name = request.POST['step_add-name'], task = task)
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
        
        if ('remind-today' in request.POST):
            ed_task.reminder = True
            ed_task.remind_time = get_remind_today(user_tz)
            ed_task.save()
            return True
        if ('remind-tomorrow' in request.POST):
            ed_task.reminder = True
            ed_task.remind_time = get_remind_tomorrow(user_tz)
            ed_task.save()
            return True
        if ('remind-next-week' in request.POST):
            ed_task.reminder = True
            ed_task.remind_time = get_remind_next_week(user_tz)
            ed_task.save()
            return True
        if ('remind-save' in request.POST):
            form_remind = TaskRemindForm(request.POST, instance = ed_task, prefix = 'task_remind_edit')
            if form_remind.is_valid():
                fr = form_remind.save(commit = False)
                ed_task.reminder = True
                ed_task.remind_time = fr.remind_time
                ed_task.save()
                return True
        if ('remind-delete' in request.POST):
            ed_task.reminder = False
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
        if ('termin-save' in request.POST):
            form_termin = TaskTerminForm(request.POST, instance = ed_task, prefix = 'task_termin_edit')
            if form_termin.is_valid():
                ft = form_termin.save(commit = False)
                ed_task.stop = ft.stop
                ed_task.save()
                return True
        if ('termin-delete' in request.POST):
            ed_task.stop = None
            if ed_task.repeat != NONE:
                ed_task.repeat = NONE
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
        if ('repeat-save' in request.POST):
            form_repeat = TaskRepeatForm(request.POST, instance = ed_task, prefix = 'task_repeat_edit')
            if form_repeat.is_valid():
                fr = form_repeat.save(commit = False)
                ed_task.repeat = fr.repeat
                ed_task.repeat_num = fr.repeat_num
                ed_task.save()
                return True
        if ('repeat-delete' in request.POST):
            ed_task.repeat = NONE
            ed_task.save()
            return True

    if not form:
        form = TaskForm(instance = ed_task, prefix = 'task_edit')

    if not form_lst:
        form_lst = TaskLstForm(instance = ed_task, prefix = 'task_lst_edit')

    if not form_info:
        form_info = TaskInfoForm(instance = ed_task, prefix = 'task_info_edit')

    if not form_file:
        form_file = TaskFilesForm()

    if not form_remind:
        form_remind = TaskRemindForm(instance = ed_task, prefix = 'task_remind_edit')

    if not form_termin:
        form_termin = TaskTerminForm(instance = ed_task, prefix = 'task_termin_edit')

    if not form_repeat:
        form_repeat = TaskRepeatForm(instance = ed_task, prefix = 'task_repeat_edit')

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
    context['task_start'] = ed_task.start
    context['task_stop'] = ed_task.stop
    context['task_d_termin'] = ed_task.d_termin()
    context['task_s_termin'] = ed_task.s_termin()
    context['task_expired'] = ed_task.b_expired()
    
    context['steps'] = Step.objects.filter(task = ed_task.id)
    context['step_form'] = StepForm(prefix = 'step_form')

    context['remind_active'] = ed_task.reminder and (ed_task.remind_time > timezone.now())
    context['task_b_remind'] = ed_task.reminder
    if ed_task.remind_time:
        context['task_remind_time'] = _('remind in').capitalize() + ' ' + ed_task.remind_time.astimezone(user_tz).strftime('%H:%M')
        context['task_remind_date'] = nice_date(ed_task.remind_time.astimezone(user_tz).date())
    context['remind_today_info'] = get_remind_today(user_tz).strftime('%H:%M')
    context['remind_tomorrow_info'] = get_remind_tomorrow(user_tz).strftime('%a, %H:%M')
    context['remind_next_week_info'] = get_remind_next_week(user_tz).strftime('%a, %H:%M')
    context['remind_form'] = form_remind

    context['termin_form'] = form_termin

    context['task_b_repeat'] = ed_task.repeat != NONE
    context['task_s_repeat'] = ed_task.s_repeat()
    context['task_repeat_days'] = ed_task.repeat_s_days()
    context['repeat_form'] = form_repeat
    context['repeat_form_d1'] = get_week_day_name(1)
    context['repeat_form_d2'] = get_week_day_name(2)
    context['repeat_form_d3'] = get_week_day_name(3)
    context['repeat_form_d4'] = get_week_day_name(4)
    context['repeat_form_d5'] = get_week_day_name(5)
    context['repeat_form_d6'] = get_week_day_name(6)
    context['repeat_form_d7'] = get_week_day_name(7)
    context['task_info'] = get_task_status(ed_task)
    return False


def get_list_details(request, context, pk):
    ed_lst = get_object_or_404(Lst.objects.filter(id = pk, user = request.user.id))
    form = None
    if (request.method == 'POST'):
        if ('list-save' in request.POST):
            form = LstForm(request.POST, instance = ed_lst, prefix = 'lst_edit')
            if form.is_valid():
                lst = form.save(commit = False)
                lst.user = request.user
                form.save()
                return True
        elif ('list-delete' in request.POST):
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
        if ('group-save' in request.POST):
            form = GrpForm(request.user, request.POST, instance = ed_grp, prefix = 'grp_edit')
            if form.is_valid():
                grp = form.save(commit = False)
                grp.user = request.user
                form.save()
                return True
        elif ('group-delete' in request.POST):
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
    
    d = task.d_termin()
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
        elif (task.d_termin() == date.today()):
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

        if (task.repeat != NONE):
            ret.append({'icon': repeat})


    if task.reminder or task.info or (len(TaskFiles.objects.filter(task = task.id)) > 0):
        if (len(ret) > 0):
            ret.append({'icon': 'separator'})
        if task.reminder:
            ret.append({'icon': 'remind'})
        if task.info:
            ret.append({'icon': 'notes'})
        if (len(TaskFiles.objects.filter(task = task.id)) > 0):
            ret.append({'icon': 'attach'})

    return ret

def find_term(data, user, grp_id):
    for term in data:
        if (term.per_grp.grp_id == grp_id):
            return term
    term = Term(user, grp_id)
    data.append(term)
    return term

def task_list(request):
    locale.setlocale(locale.LC_CTYPE, request.LANGUAGE_CODE)
    locale.setlocale(locale.LC_TIME, request.LANGUAGE_CODE)

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
                if not task.stop:
                  task.stop = date.today()
                task.completion = timezone.now()
            else:
                task.completion = None
            task.save()
            return HttpResponseRedirect(reverse('todo:task_list'))
        if 'task-in-list-important' in request.POST:
            task = Task.objects.filter(id = request.POST['task-in-list-important']).get()
            task.important = not task.important
            task.save()
            return HttpResponseRedirect(reverse('todo:task_list'))
        if 'task-add' in request.POST:
            task = Task.objects.create(user = request.user, name = request.POST['task_add-name'], \
                                       lst = param.lst, in_my_day = (param.cur_view == MY_DAY), important = (param.cur_view == IMPORTANT))
            return HttpResponseRedirect(reverse('todo:task_form', args = [task.id]))
        if 'list-add' in request.POST:
            lst = Lst.objects.create(user = request.user, name = request.POST['name'])
            return HttpResponseRedirect(reverse('todo:list_form', args = [lst.id]))
        if 'group-add' in request.POST:
            grp = Grp.objects.create(user = request.user, name = request.POST['name'])
            return HttpResponseRedirect(reverse('todo:group_form', args = [grp.id]))

    context = todo_base_context(request, param.cur_view, param.lst)

    details_mode = ''
    redirect = False
    if (param.details_mode == TASK_DETAILS):
        if not Task.objects.filter(id = param.details_pk, user = request.user.id).exists():
            param.details_mode = NONE
            param.save()
            redirect = True
        else:
            details_mode = 'task'
            user_tz = pytz.timezone('Europe/Minsk')
            redirect = get_task_details(request, context, param.details_pk, param.lst, user_tz)
    elif (param.details_mode == LIST_DETAILS):
        if not Lst.objects.filter(id = param.details_pk, user = request.user.id).exists():
            param.details_mode = NONE
            param.save()
            redirect = True
        else:
            details_mode = 'list'
            redirect = get_list_details(request, context, param.details_pk)
    elif (param.details_mode == GROUP_DETAILS):
        if not Grp.objects.filter(id = param.details_pk, user = request.user.id).exists():
            param.details_mode = NONE
            param.save()
            redirect = True
        else:
            details_mode = 'group'
            redirect = get_group_details(request, context, param.details_pk)

    if redirect:
        return HttpResponseRedirect(reverse('todo:task_list'))

    context['details_mode'] = details_mode
    context['details_pk'] = param.details_pk

    data = []
    if (param.cur_view != PLANNED):
        term = Term(request.user, GRP_PLANNED_NONE)
        data.append(term)

    for task in sorted_tasks(request.user, param.cur_view, param.lst):
        if (param.cur_view == PLANNED):
            grp_id = get_grp_planned(task.d_termin())
            term = find_term(data, request.user, grp_id)
        term.todo.append([task, get_task_info(task, param.cur_view)])
    
    context['object_list'] = sorted(data, key=lambda term: term.per_grp.grp_id)
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

def period_toggle(request, pk):
    per_grp = get_object_or_404(PerGrp.objects.filter(user = request.user.id, grp_id = pk))
    per_grp.is_open = not per_grp.is_open
    per_grp.save()
    return HttpResponseRedirect(reverse('todo:task_list'))

