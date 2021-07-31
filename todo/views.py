import time
import os, locale
from datetime import datetime, timedelta, date

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import UpdateView, CreateView
from django.core.paginator import Paginator
from django.urls import reverse

from rusel.context import get_base_context
from rusel.aside import Fix, Sort
from rusel.content import find_group
from rusel.utils import extract_get_params
from task.models import Task, Step, Group, TaskGroup
from task.views import GroupDetailView
from task.const import *
from todo.const import *
from todo.utils import get_grp_planned, GRPS_PLANNED, get_week_day_name
from todo.forms import CreateTaskForm, TaskForm

list_url = '/todo/'
app_name = 'todo'

def toggle_completed(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user.id)
    task.toggle_completed()
    return HttpResponseRedirect(reverse('todo:task-list') + extract_get_params(request))

def toggle_important(request, pk):
    task = get_object_or_404(Task, id=pk, user=request.user.id)
    task.important = not task.important
    task.save()
    return HttpResponseRedirect(reverse('todo:task-list') + extract_get_params(request))

class TaskAside():

    def get_aside_context(self, user):
        fixes = []
        fixes.append(Fix('myday', _('my day').capitalize(), 'todo/icon/myday.png', list_url+'?view='+MY_DAY, len(get_tasks(user, MY_DAY, 0).exclude(completed = True))))
        fixes.append(Fix('important', _('important').capitalize(), 'todo/icon/important.png', list_url+'?view='+IMPORTANT, len(get_tasks(user, IMPORTANT, 0))))
        fixes.append(Fix('planned', _('planned').capitalize(), 'todo/icon/planned.png', list_url+'?view='+PLANNED, len(get_tasks(user, PLANNED, 0))))
        fixes.append(Fix('all', _('all').capitalize(), 'rok/icon/all.png', list_url, len(get_tasks(user, ALL, 0))))
        fixes.append(Fix('completed', _('completed').capitalize(), 'todo/icon/completed.png', list_url+'?view='+COMPLETED, len(get_tasks(user, COMPLETED, 0))))
        return fixes


class TaskListView(TaskAside, CreateView):
    model = Task
    pagenate_by = 10
    template_name = 'base/list.html'
    view_id = ALL
    title = _('unknown')
    view_as_tree = False
    form_class = CreateTaskForm
    cur_grp = 0

    def get_queryset(self):
        if (self.view_id == MY_DAY):
            return Task.objects.filter(user=self.request.user, app_task=TASK, in_my_day=True).order_by('created')
        if (self.view_id == IMPORTANT):
            return Task.objects.filter(user=self.request.user, app_task=TASK, important=True, completed=False).order_by('created')
        if (self.view_id == PLANNED):
            return Task.objects.filter(user=self.request.user, app_task=TASK, completed=False).exclude(stop=None).order_by('created')
        if (self.view_id == COMPLETED):
            return Task.objects.filter(user=self.request.user, app_task=TASK, completed=True).order_by('created')
        if (self.view_id == LIST_MODE):
            return [tg.task for tg in TaskGroup.objects.filter(group=self.cur_grp)]
        # ALL
        return Task.objects.filter(user=self.request.user, app_task=TASK, completed=False).order_by('created')

    def get_success_url(self):
        url = super().get_success_url()
        return url + extract_get_params(self.request)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.app_task = TASK
        ret = super().form_valid(form)
        l = self.request.GET.get('lst')
        if l:
            lst = Group.objects.filter(id=l).get()
            TaskGroup.objects.create(task=form.instance, group=lst, app=app_name)
        return ret
    
    def get_context_data(self, **kwargs):
        start = time.time()
        context = super().get_context_data(**kwargs)
        self.init_view()
        title = self.get_title()
        gp = self.get_group_path()
        context['group_path'] = gp
        if gp and not title:
            title = ' / '.join([x['name'] for x in gp])
        context.update(get_base_context(self.request, app_name, False, title))
        context['fix_list'] = self.get_aside_context(self.request.user)
        context['sort_options'] = self.get_sorts()
        context['view_id'] = self.view_id
        context['params'] = extract_get_params(self.request)
        context['item_detail_url'] = app_name + ':item-detail'

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
        if self.view_as_tree:
            for task in tasks:
                grp_id = get_grp_planned(self.view_id, task.stop.date() if task.stop else None, task.completed)
                group = find_group(groups, grp_id, GRPS_PLANNED[grp_id].capitalize())
                group.items.append(task)
            context['item_groups'] = sorted(groups, key = lambda group: group.id)
        else:    
            paginator = Paginator(tasks, ITEMS_PER_PAGE)
            page_obj = paginator.get_page(page_number)
            context['page_obj'] = paginator.get_page(page_number)
        context['profiling'] = "Time: %.03f s" % (time.time() - start)
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

        self.view_as_tree = (self.view_id == MY_DAY) or (self.view_id == PLANNED) or (self.view_id == LIST_MODE)
            
        if self.view_as_tree:
            self.template_name = 'base/tree.html'
        else:
            self.template_name = 'base/list.html'
        
    def get_title(self):
        if (self.view_id == MY_DAY):
            return _('my day').capitalize()
        if (self.view_id == IMPORTANT):
            return _('important').capitalize()
        if (self.view_id == PLANNED):
            return _('planned').capitalize()
        if (self.view_id == ALL) or (self.view_id == ''):
            return _('all').capitalize()
        if (self.view_id == COMPLETED):
            return _('completed').capitalize()
        if (self.view_id == LIST_MODE):
            return ''
        return '???'
        
    def get_group_path(self):
        ret = []
        if (self.view_id == LIST_MODE) and self.cur_grp:
            grp = Group.objects.filter(id=self.cur_grp).get()
            ret.append({'id': grp.id, 'name': grp.name, 'url': grp.url})
            parent = grp.node
            while parent:
                grp = Group.objects.filter(id=parent.id).get()
                ret.append({'id': grp.id, 'name': grp.name, 'url': grp.url})
                parent = grp.node
        return ret
    
    def get_sorts(self):
        sorts = []
        if (self.view_id == MY_DAY):
            sorts.append(Sort('important', _('by importance').capitalize(), 'todo/icon/important.png'))
            sorts.append(Sort('termin', _('by termin date').capitalize(), 'todo/icon/planned.png'))
            sorts.append(Sort('name',  _('by name').capitalize(), 'todo/icon/sort.png'))
            sorts.append(Sort('created',  _('by creation date').capitalize(), 'todo/icon/created.png'))
        return sorts

"""
================================================================
"""

class TaskDetailView(TaskAside, UpdateView):
    model = Task
    template_name = 'todo/task_detail.html'
    title = _('unknown')
    form_class = TaskForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.get_object()
        context.update(get_base_context(self.request, app_name, True, item.name))
        context['params'] = extract_get_params(self.request)
        context['fix_list'] = self.get_aside_context(self.request.user)
        context['ed_item'] = self.object
        context['task_actual'] = (not self.object.completed) and (not self.object.b_expired()) and self.object.stop
        context['steps'] = Step.objects.filter(task=self.object.id)
        
        # this is needed to translate the names of the days of the week
        locale.setlocale(locale.LC_CTYPE, self.request.LANGUAGE_CODE)
        locale.setlocale(locale.LC_TIME, self.request.LANGUAGE_CODE)
        
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
        return context


"""
================================================================
"""

class TaskGroupDetailView(TaskAside, GroupDetailView):

    def get_success_url(self):
        return reverse('todo:group-detail', args=[self.get_object().id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        context['fix_list'] = self.get_aside_context(self.request.user)
        context['return_url'] = list_url
        return context


"""
================================================================
"""


def get_tasks(user, mode, grp_id):
    ret = None
    if (mode == MY_DAY):
        ret = Task.objects.filter(user=user.id, app_task=TASK, in_my_day=True)
    elif (mode == IMPORTANT):
        ret = Task.objects.filter(user=user.id, app_task=TASK, important=True).exclude(completed=True)
    elif (mode == PLANNED):
        ret = Task.objects.filter(user=user.id, app_task=TASK).exclude(stop=None).exclude(completed=True)
    elif (mode == COMPLETED):
        ret = Task.objects.filter(user=user.id, app_task=TASK, completed=True)
    elif (mode == LIST_MODE):
        if Group.objects.filter(id=grp_id).exists():
            ret = Group.objects.filter(id=grp_id).get().consist
    else: # ALL or NONE
        ret = Task.objects.filter(user=user.id, app_task=TASK).exclude(completed=True)
    return ret

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


