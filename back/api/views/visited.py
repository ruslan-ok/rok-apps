from rest_framework import viewsets, permissions, renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from api.serializers.visited import VisitedHistorySerializer
from task.models import VisitedHistory


class VisitedViewSet(viewsets.ModelViewSet):
    serializer_class = VisitedHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def get_queryset(self):
        return VisitedHistory.objects.filter(user=self.request.user.id).order_by('-stamp')

    @action(detail=True)
    def toggle_pin(self, request, pk=None):
        visited = self.get_object()
        visited.pinned = not visited.pinned
        visited.save()
        serializer = VisitedHistorySerializer(instance=visited, context={'request': request})
        return Response(serializer.data)
