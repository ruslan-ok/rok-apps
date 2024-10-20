from rest_framework import permissions, renderers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from task.models import Task, TaskGroup, TaskRoleInfo, Urls, Step
from task.const import APP_TODO, NUM_ROLE_TODO, ROLE_TODO
from api.serializers.todo import TodoSerializer


class TodoViewSet(ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.JSONRenderer, renderers.BrowsableAPIRenderer,]
    pagination_class = None

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return None
        queryset = Task.objects.filter(user=self.request.user.id, app_task=NUM_ROLE_TODO)
        group_id = self.request.query_params.get('group')
        if group_id is not None:
            tgs = TaskGroup.objects.filter(group=int(group_id), role=ROLE_TODO)
            queryset = queryset.filter(id__in=[x.task.id for x in tgs])
            return queryset
        view_id = self.request.query_params.get('view', 'planned')
        if view_id is not None:
            if (view_id == 'myday'):
                return queryset.filter(in_my_day=True).exclude(completed=True)
            if (view_id == 'important'):
                return queryset.filter(important=True).exclude(completed=True)
            if (view_id == 'planned'):
                return queryset.exclude(stop=None).exclude(completed=True)
            if (view_id == 'completed'):
                return queryset.filter(completed=True)
        return queryset

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def extra(request, pk):
    app = request.query_params.get('app', APP_TODO)
    role = request.query_params.get('role', ROLE_TODO)
    group_name = ''
    tgs = TaskGroup.objects.filter(task=pk, role=role)
    if (len(tgs) > 0):
        tg = tgs[0]
        group = tg.group
        if group:
            group_name = group.name
    has_files = False
    if TaskRoleInfo.objects.filter(task=pk, app=app, role=role).exists():
        ti = TaskRoleInfo.objects.filter(task=pk, app=app, role=role).get()
        if ti and ti.files_qnt is not None:
            has_files = ti.files_qnt > 0
    has_links = len(Urls.objects.filter(task=pk)) > 0
    step_total = step_completed = 0
    for step in Step.objects.filter(task=pk):
        step_total += 1
        if step.completed:
            step_completed += 1

    data = {
        'roles': [],
        'params': '',
        'group_name': group_name,
        'attributes': [],
        'remind_active': False,
        'step_completed': step_completed,
        'step_total': step_total,
        'has_files': has_files,
        'has_links': has_links,
    }
    return Response(data)
