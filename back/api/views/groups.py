from rest_framework import permissions, renderers
from rest_framework.viewsets import ModelViewSet
from task.models import Group
from api.serializers.group import GroupSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class GroupViewSet(ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return None
        app = self.request.query_params.get('app')
        role = self.request.query_params.get('role')
        queryset = Group.objects.filter(user=self.request.user, app=app, role=role)
        return queryset

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def groups_test(request):
    data = [
        {
            'id': 1,
            'node_id': None,
            'name': 'name-1',
            'act_items_qty': 10,
        },
        {
            'id': 2,
            'node_id': 5,
            'name': 'name-2.2',
            'act_items_qty': 10,
        },
        {
            'id': 3,
            'node_id': 5,
            'name': 'name-2.1',
            'act_items_qty': 10,
        },
        {
            'id': 4,
            'node_id': None,
            'name': 'name-3',
            'act_items_qty': 10,
        },
        {
            'id': 5,
            'node_id': None,
            'name': 'name-2',
            'act_items_qty': 10,
        },
    ]
    return Response(data)
