from rest_framework import viewsets, permissions, renderers
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers import ApartSerializer
from apart.models import Apart

class ApartViewSet(viewsets.ModelViewSet):
    serializer_class = ApartSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def get_queryset(self):
        return Apart.objects.filter(user=self.request.user).order_by('name')
    
    @action(detail=True)
    def set_active(self, request, pk=None):
        for apart in Apart.objects.filter(user=self.request.user.id, active=True).exclude(id=pk):
            apart.active = False
            apart.save()
        apart = self.get_object()
        apart.active = True
        apart.save()
        serializer = ApartSerializer(instance=apart, context={'request': request}, many=False)
        return Response(serializer.data)
