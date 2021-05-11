from django.utils.translation import gettext_lazy as _

from rusel.apps import get_app_params
from hier.aside import Fix, Sort
from task.models import ATask
from task.views import ATaskViewSet
from task.const import *
from todo.const import *

class TodoViewSet(ATaskViewSet):
    app = 'todo'
    title = _('unknown')
    mode = ALL
    cur_group = 0

    def get_queryset(self):
        if (self.mode == MY_DAY):
            return ATask.objects.filter(user=self.request.user, app_task=TASK, in_my_day=True)
        elif (self.mode == IMPORTANT):
            return ATask.objects.filter(user=self.request.user, app_task=TASK, important=True).exclude(completed=True)
        elif (self.mode == PLANNED):
            return ATask.objects.filter(user=self.request.user, app_task=TASK).exclude(stop=None).exclude(completed=True)
        elif (self.mode == COMPLETED):
            return ATask.objects.filter(user=self.request.user, app_task=TASK, completed=True)
        elif (self.mode == LIST_MODE):
            return ATask.objects.filter(user=self.request.user, app_task=TASK, grp=self.cur_group)
        else: # ALL or NONE
            return ATask.objects.filter(user=self.request.user, app_task=TASK).exclude(completed=True)

    def extra_context(self, context):
        super().extra_context(context)

        fixes = []
        fixes.append(Fix('myday', _('my day').capitalize(), 'todo/icon/myday.png', '/drf/todo/myday/', len(get_tasks(self.request.user, MY_DAY, 0).exclude(completed = True))))
        fixes.append(Fix('important', _('important').capitalize(), 'todo/icon/important.png', 'important/', len(get_tasks(self.request.user, IMPORTANT, 0))))
        fixes.append(Fix('planned', _('planned').capitalize(), 'todo/icon/planned.png', 'planned/', len(get_tasks(self.request.user, PLANNED, 0))))
        fixes.append(Fix('all', _('all').capitalize(), 'rok/icon/all.png', '/drf/todo/', len(get_tasks(self.request.user, ALL, 0))))
        fixes.append(Fix('completed', _('completed').capitalize(), 'todo/icon/completed.png', 'completed/', len(get_tasks(self.request.user, COMPLETED, 0))))
        context['fix_list'] = fixes
        context['list'] = self.filter_queryset(self.get_queryset())
        
        sorts = []
        app_param = get_app_params(self.request.user, self.app)
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
        context['title'] = self.title

    def all(self, request, *args, **kwargs):
        self.mode = ALL
        return list(self, request, args, kwargs)

    def by_group(self, request, pk, *args, **kwargs):
        self.mode = LIST_MODE
        self.cur_group = pk
        return list(self, request, args, kwargs)


def get_tasks(user, mode, lst_id):
    if (mode == MY_DAY):
        ret = ATask.objects.filter(user=user.id, app_task=TASK, in_my_day=True)
    elif (mode == IMPORTANT):
        ret = ATask.objects.filter(user=user.id, app_task=TASK, important=True).exclude(completed=True)
    elif (mode == PLANNED):
        ret = ATask.objects.filter(user=user.id, app_task=TASK).exclude(stop=None).exclude(completed=True)
    elif (mode == COMPLETED):
        ret = ATask.objects.filter(user=user.id, app_task=TASK, completed=True)
    elif (mode == LIST_MODE):
        ret = ATask.objects.filter(user=user.id, app_task=TASK, lst=lst_id)
    else: # ALL or NONE
        ret = ATask.objects.filter(user=user.id, app_task=TASK).exclude(completed=True)
    return ret

class TodoAllViewSet(TodoViewSet):
    mode = ALL
    title = _('all')

    def get_queryset(self):
        return ATask.objects.filter(user=self.request.user, app_task=TASK).exclude(completed=True)

class TodoMydayViewSet(TodoViewSet):
    mode = MY_DAY
    title = _('my day')

    def get_queryset(self):
        return ATask.objects.filter(user=self.request.user, app_task=TASK, in_my_day=True)



