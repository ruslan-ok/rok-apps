from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from task.models import Group

@api_view(['POST'])
@permission_classes([])
@authentication_classes([])
def toggle_sub_group(request, pk):
    sub_group_id = request.POST.get('sub_group_id')
    if pk and sub_group_id:
        group = Group.objects.filter(id=pk).get()
        group.toggle_sub_group(sub_group_id)
        return Response({'ok': True})
