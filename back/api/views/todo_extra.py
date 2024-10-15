from django.shortcuts import get_object_or_404
# from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from task.const import APP_TODO, ROLE_TODO
from task.models import Task, TaskGroup, TaskRoleInfo, Urls, Step

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

@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def completed(request, pk):
    task = get_object_or_404(Task.objects.filter(user=request.user.id, id=pk))
    task.toggle_completed(do_complete=True)
    return Response({'result': 'ok'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([SessionAuthentication])
def important(request, pk):
    task = get_object_or_404(Task.objects.filter(user=request.user.id, id=pk))
    task.important = not task.important
    task.save()
    return Response({'result': 'ok'})
