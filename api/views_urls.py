from rest_framework import viewsets, permissions, renderers, pagination
from api.serializers import UrlsSerializer
from task.models import Urls

class UrlsViewSet(viewsets.ModelViewSet):
    serializer_class = UrlsSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        return Urls.objects.all().order_by('-created')
