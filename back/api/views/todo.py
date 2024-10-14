from rest_framework import permissions, renderers
from rest_framework.viewsets import ModelViewSet
from task.models import Task, TaskGroup
from task.const import NUM_ROLE_TODO, ROLE_TODO
from api.serializers.todo import TodoSerializer

class TodoViewSet(ModelViewSet):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
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
