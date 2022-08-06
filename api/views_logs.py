from datetime import datetime
from rest_framework import viewsets, permissions, renderers, status, pagination
from rest_framework.decorators import action
from rest_framework.response import Response

from logs.models import ServiceEvent
from api.serializers import LogsSerializer
from task.const import *

class LogsViewSet(viewsets.ModelViewSet):
    serializer_class = LogsSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        data = ServiceEvent.objects.all().order_by('-created')
        if 'device' in self.request.GET:
            device = self.request.GET['device']
            data = data.filter(device=device)
        if 'app' in self.request.GET:
            app = self.request.GET['app']
            data = data.filter(app=app)
            if 'service' in self.request.GET:
                service = self.request.GET['service']
                data = data.filter(service=service)
        if 'day' in self.request.GET:
            day_str = self.request.GET['day']
            day = datetime.strptime(day_str, '%Y%m%d')
            data = data.filter(created__date=day)
        return data

