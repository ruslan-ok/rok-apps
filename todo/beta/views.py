import locale
from datetime import datetime, timedelta

from django.utils.translation import gettext_lazy as _
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.core.paginator import Paginator
from django.urls import reverse

from rusel.context import get_base_context
from hier.aside import Fix, Sort
from hier.content import find_group
from task.models import Task, Step, Group, TaskGroup
from task.const import *
from todo.const import *
from todo.utils import get_grp_planned, GRPS_PLANNED, get_week_day_name
from todo.beta.forms import TaskForm

class TaskAside():

    def get_aside_context(self, user):
        fixes = []
        fixes.append(Fix('myday', _('my day').capitalize(), 'todo/icon/myday.png', '/beta/todo/myday/', len(get_tasks(user, MY_DAY, 0).exclude(completed = True))))
        fixes.append(Fix('important', _('important').capitalize(), 'todo/icon/important.png', '/beta/todo/important/', len(get_tasks(user, IMPORTANT, 0))))
        fixes.append(Fix('planned', _('planned').capitalize(), 'todo/icon/planned.png', '/beta/todo/planned/', len(get_tasks(user, PLANNED, 0))))
        fixes.append(Fix('all', _('all').capitalize(), 'rok/icon/all.png', '/beta/todo/', len(get_tasks(user, ALL, 0))))
        fixes.append(Fix('completed', _('completed').capitalize(), 'todo/icon/completed.png', '/beta/todo/completed/', len(get_tasks(user, COMPLETED, 0))))
        return fixes


class TaskListView(TaskAside, ListView):
    model = Task
    pagenate_by = 10
    template_name = 'todo/beta/atask_list.html'
    app = 'todo'
    view_id = ''
    title = _('unknown')
    mode = ALL
    view_as_tree = False

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, app_task=TASK)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_base_context(self.request, self.app, False, self.title.capitalize()))
        context['fix_list'] = self.get_aside_context(self.request.user)
        context['sort_options'] = self.get_sorts()
        context['view_id'] = self.view_id

        groups = []
        query = None
        page_number = 1
        if self.request.method == 'GET':
            query = self.request.GET.get('q')
            page_number = self.request.GET.get('page')
        search_mode = 0
    
        tasks = self.get_queryset()
        if self.view_as_tree:
            for task in tasks:
                grp_id = get_grp_planned(self.mode, task.stop, task.completed)
                group = find_group(groups, self.request.user, self.app, grp_id, GRPS_PLANNED[grp_id].capitalize())
                group.items.append(task)
            context['item_groups'] = sorted(groups, key = lambda group: group.grp.grp_id)
        else:    
            paginator = Paginator(tasks, ITEMS_PER_PAGE)
            page_obj = paginator.get_page(page_number)
            context['page_obj'] = paginator.get_page(page_number)
        return context

    def get_sorts(self):
        return []

class MyDayListView(TaskListView):
    title = _('my day')
    view_as_tree = True
    template_name = 'todo/beta/atask_tree.html'
    mode = MY_DAY
    view_id = 'myday'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, app_task=TASK, in_my_day=True)

    def get_sorts(self):
        sorts = []
        sorts.append(Sort('important', _('by importance').capitalize(), 'todo/icon/important.png'))
        sorts.append(Sort('termin', _('by termin date').capitalize(), 'todo/icon/planned.png'))
        sorts.append(Sort('name',  _('by name').capitalize(), 'todo/icon/sort.png'))
        sorts.append(Sort('created',  _('by creation date').capitalize(), 'todo/icon/created.png'))
        return sorts

class ImportantListView(TaskListView):
    title = _('important')
    mode = IMPORTANT
    view_id = 'important'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, app_task=TASK, important=True).exclude(completed=True)

    def get_sorts(self):
        sorts = []
        return sorts

class PlannedListView(TaskListView):
    title = _('planned')
    view_as_tree = True
    template_name = 'todo/beta/atask_tree.html'
    mode = PLANNED
    view_id = 'planned'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, app_task=TASK).exclude(stop=None).exclude(completed=True)

    def get_sorts(self):
        sorts = []
        return sorts

class AllListView(TaskListView):
    title = _('all')
    mode = ALL

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, app_task=TASK).exclude(completed=True)

    def get_sorts(self):
        sorts = []
        return sorts

class CompletedListView(TaskListView):
    title = _('completed')
    mode = COMPLETED
    view_id = 'completed'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user, app_task=TASK, completed=True)

    def get_sorts(self):
        sorts = []
        return sorts

class ByGroupListView(TaskListView):
    cur_grp = None
    mode = LIST_MODE
    view_id = 'bygroup'

    def get_queryset(self):
        return [tg.task for tg in TaskGroup.objects.filter(group=self.cur_grp)]

    def get_sorts(self):
        sorts = []
        return sorts

    def get(self, request, *args, **kwargs):
        self.cur_grp = kwargs['grp']
        self.view_id = 'bygroup/' + str(self.cur_grp)
        if Group.objects.filter(id=self.cur_grp).exists():
            grp = Group.objects.filter(id=self.cur_grp).get()
            self.title = grp.name
            parent = grp.node
            while parent:
                grp = Group.objects.filter(id=parent.id).get()
                self.title = grp.name + ' \\ ' + self.title
                parent = grp.node
        return super().get(request, *args, **kwargs)



class TaskDetailView(TaskAside, UpdateView):
    model = Task
    template_name = 'todo/beta/atask_detail.html'
    app = 'todo'
    title = _('unknown')
    mode = ALL
    form_class = TaskForm

    def get_success_url(self):
        return reverse('todo_beta:all-detail', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        context.update(get_base_context(self.request, self.app, True, task.name))
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

class MyDayDetailView(TaskDetailView):
    pass

class ImportantDetailView(TaskDetailView):
    pass

class PlannedDetailView(TaskDetailView):
    pass

class AllDetailView(TaskDetailView):
    pass

class CompletedDetailView(TaskDetailView):
    pass

class ByGroupDetailView(TaskDetailView):
    cur_grp = None

    """
    def get(self, request, *args, **kwargs):
        self.cur_grp = kwargs['grp']
        if Group.objects.filter(id=self.cur_grp).exists():
            grp = Group.objects.filter(id=self.cur_grp).get()
            up_title = grp.name
            parent = grp.node
            while parent:
                grp = Group.objects.filter(id=parent.id).get()
                up_title = grp.name + ' \\ ' + up_title
                parent = grp.node
        task = self.get_object()
        self.title = up_title + ' \\ ' + task.name
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
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

