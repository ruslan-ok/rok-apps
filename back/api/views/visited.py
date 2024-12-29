from rest_framework import permissions, renderers
from rest_framework.viewsets import ModelViewSet

from task.models import VisitedHistory
from api.serializers.visited import VisitedDetailsSerializer


class VisitedViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.JSONRenderer, renderers.BrowsableAPIRenderer,]
    serializer_class = VisitedDetailsSerializer
    pagination_class = None

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return None
        queryset = VisitedHistory.objects.filter(user=self.request.user.pk)
        return queryset
