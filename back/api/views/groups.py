from rest_framework import permissions, renderers
from rest_framework.viewsets import ModelViewSet

from task.models import Group
from api.serializers.group import GroupSerializer


class GroupViewSet(ModelViewSet):
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.JSONRenderer, renderers.BrowsableAPIRenderer,]
    pagination_class = None

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return None
        app = self.request.query_params.get('app', 'todo')
        role = self.request.query_params.get('role')
        queryset = Group.objects.filter(user=self.request.user)
        if app:
            queryset = queryset.filter(app=app)
        if role:
            queryset = queryset.filter(role=role, determinator=None)
        return queryset
