from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from task.const import APP_TODO, ROLE_TODO
from task.models import TaskGroup, TaskRoleInfo, Urls, Step

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def todo_extra(request, pk):
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