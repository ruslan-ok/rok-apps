from rest_framework import permissions, renderers
from rest_framework.viewsets import ModelViewSet

from task.models import Task
from task.const import NUM_ROLE_MARKER
from api.serializers.weight import WeightSerializer


class WeightViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.JSONRenderer, renderers.BrowsableAPIRenderer,]
    serializer_class = WeightSerializer
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        print(serializer)
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return None
        queryset = Task.objects.filter(user=self.request.user.id, app_health=NUM_ROLE_MARKER)
        return queryset
