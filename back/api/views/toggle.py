from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from task.models import Group

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def toggle_sub_group(request):
    group_id = request.query_params.get('group_id')
    sub_group_id = request.query_params.get('sub_group_id')
    if group_id and sub_group_id:
        group = Group.objects.filter(id=group_id).get()
        group.toggle_sub_group(sub_group_id)
        return Response({'ok': True})
