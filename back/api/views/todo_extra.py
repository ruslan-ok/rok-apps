from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from task.models import TaskGroup, Group

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def todo_extra(request, pk):
    group_name = ''
    tgs = TaskGroup.objects.filter(task=pk, role='todo')
    if (len(tgs) > 0):
        tg = tgs[0]
        group = tg.group
        if group:
            group_name = group.name
    data = {
        'roles': [],
        'absolute_url': '',
        'params': '',
        'group_name': group_name,
        'attributes': [],
        'remind_active': False,
        'step_completed': 0,
        'step_total': 0,
    }
    return Response(data)