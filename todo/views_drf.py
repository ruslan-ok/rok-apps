from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from rest_framework.response import Response

from rusel.apps import get_app_params
from rusel.context import get_base_context
from hier.aside import Fix, Sort
from hier.params import get_search_mode, get_search_info
from hier.content import find_group
from task.models import TaskGrp, ATask
from task.views import ATaskViewSet
from task.const import *
from todo.const import *
from todo.utils import get_grp_planned, GRPS_PLANNED

class TodoViewSet(ATaskViewSet):
    app = 'todo'
    title = _('unknown')
    mode = ALL
    cur_list = 0

    def get_queryset(self):
        return ATask.objects.filter(user=self.request.user, app_task=TASK, completed=False)

    def detail_view(self):
        if (self.mode == ALL):
            return 'atask-detail'
        return self.app + '-' + self.mode + '-detail'
    
    def list_view(self):
        if (self.mode == ALL):
            return 'atask-list'
        return self.app + '-' + self.mode + '-list'
    
    def extra_context(self, context):
        super().extra_context(context)

        fixes = []
        fixes.append(Fix('myday', _('my day').capitalize(), 'todo/icon/myday.png', '/drf/myday/', len(get_tasks(self.request.user, MY_DAY, 0).exclude(completed = True))))
        fixes.append(Fix('important', _('important').capitalize(), 'todo/icon/important.png', '/drf/important/', len(get_tasks(self.request.user, IMPORTANT, 0))))
        fixes.append(Fix('planned', _('planned').capitalize(), 'todo/icon/planned.png', '/drf/planned/', len(get_tasks(self.request.user, PLANNED, 0))))
        fixes.append(Fix('all', _('all').capitalize(), 'rok/icon/all.png', '/drf/todo/', len(get_tasks(self.request.user, ALL, 0))))
        fixes.append(Fix('completed', _('completed').capitalize(), 'todo/icon/completed.png', '/drf/completed/', len(get_tasks(self.request.user, COMPLETED, 0))))
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

        groups = []
        query = None
        if self.request.method == 'GET':
            query = self.request.GET.get('q')
        search_mode = 0
    
        tasks = self.sorted_tasks(self.request.user, query)
        if self.view_as_tree:
            for task in tasks:
                grp_id = get_grp_planned(self.mode, task.stop, task.completed)
                group = find_group(groups, self.request.user, self.app, grp_id, GRPS_PLANNED[grp_id].capitalize())
                group.items.append(task)
            context['item_groups'] = sorted(groups, key = lambda group: group.grp.grp_id)
        else:    
            context['page_obj'] = tasks
        context['search_info'] = get_search_info(query)
        context['search_qty'] = len(tasks)
        context['search_data'] = query and (len(tasks) > 0)

    def sorted_tasks(self, user, query):
        data = self.get_filtered_tasks(user, query)
        return data # TODO: sort

    def get_filtered_tasks(self, user, query):
        ret = self.get_queryset()
        search_mode = get_search_mode(query)
        lookups = None
        if (search_mode == 0):
            return ret
        elif (search_mode == 1):
            lookups = Q(name__icontains=query) | Q(info__icontains=query)
        elif (search_mode == 2):
            lookups = Q(categories__icontains=query[1:])
        return ret.filter(lookups)

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
        ret = ATask.objects.filter(user=user.id, app_task=TASK, grp=lst_id)
    else: # ALL or NONE
        ret = ATask.objects.filter(user=user.id, app_task=TASK).exclude(completed=True)
    return ret

class MyDayViewSet(TodoViewSet):
    mode = MY_DAY
    title = _('my day')
    view_as_tree = True

    def get_queryset(self):
        return ATask.objects.filter(user=self.request.user, app_task=TASK, in_my_day=True)

class ImportantViewSet(TodoViewSet):
    mode = IMPORTANT
    title = _('important')

    def get_queryset(self):
        return ATask.objects.filter(user=self.request.user, app_task=TASK, important=True).exclude(completed=True)

    def create(self, request, *args, **kwargs):
        if self.native(request):
            return super(ATaskViewSet, self).create(request, *args, **kwargs)

        serializer = self.get_serializer(data={'name': request.data['item_add-name']})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        serializer.instance.important = True
        serializer.instance.save()
        return HttpResponseRedirect(str(serializer.instance.id) + '/')

class PlannedViewSet(TodoViewSet):
    mode = PLANNED
    title = _('planned')
    view_as_tree = True

    def get_queryset(self):
        return ATask.objects.filter(user=self.request.user, app_task=TASK).exclude(stop=None).exclude(completed=True)

class AllViewSet(TodoViewSet):
    mode = ALL
    title = _('all')

    def get_queryset(self):
        return ATask.objects.filter(user=self.request.user, app_task=TASK).exclude(completed=True)

class CompletedViewSet(TodoViewSet):
    mode = COMPLETED
    title = _('completed')

    def get_queryset(self):
        return ATask.objects.filter(user=self.request.user, app_task=TASK, completed=True)

class ByListViewSet(TodoViewSet):
    mode = LIST_MODE
    title = _('by list')

    def get_queryset(self):
        return ATask.objects.filter(user=self.request.user, app_task=TASK, grp=self.cur_list)

    def list(self, request, list_pk, *args, **kwargs):
        self.cur_list = list_pk
        if self.native(request):
            return super(ATaskViewSet, self).list(request, *args, **kwargs)

        if TaskGrp.objects.filter(id=list_pk).exists():
            self.title = TaskGrp.objects.filter(id=list_pk).get().name

        context = get_base_context(request, self.app, False, self.app_name())
        self.extra_context(context)
        return Response(context, template_name=self.get_template_name())

    def retrieve(self, request, list_pk, pk, *args, **kwargs):
        self.cur_list = list_pk
        if self.native(request):
            return super(ATaskViewSet, self).retrieve(request, *args, **kwargs)

        if TaskGrp.objects.filter(id=list_pk).exists():
            self.title = TaskGrp.objects.filter(id=list_pk).get().name

        context = get_base_context(request, self.app, True, self.app_name())
        self.extra_context(context)
        context['serializer'] = self.get_serializer(self.get_object())
        return Response(context, template_name=self.get_template_name())
    


