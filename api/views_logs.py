import requests, json
from datetime import datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, renderers

from logs.models import EventType, ServiceEvent
from api.serializers import LogsSerializer
from task.const import *

class LogsViewSet(viewsets.ModelViewSet):
    serializer_class = LogsSerializer
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [renderers.BrowsableAPIRenderer, renderers.JSONRenderer,]
    pagination_class = None

    def perform_create(self, serializer):
        event = serializer.save()
        if 'one_per_day' in serializer.initial_data:
            one_per_day = serializer.initial_data['one_per_day']
            if one_per_day == 'True':
                ServiceEvent.objects.filter(device=event.device, app=event.app, service=event.service, type=event.type, name=event.name, info=event.info).exclude(id=event.id).delete()

    def get_queryset(self):
        order_by = '-created'
        if 'order_by' in self.request.GET:
            order_by = self.request.GET['order_by']
        data = ServiceEvent.objects.all().order_by(order_by, '-id')
        if 'device' in self.request.GET:
            device = self.request.GET['device']
            data = data.filter(device=device)
        if 'app' in self.request.GET:
            app = self.request.GET['app']
            data = data.filter(app=app)
            if 'service' in self.request.GET:
                service = self.request.GET['service']
                data = data.filter(service=service)
        if 'type' in self.request.GET:
            type = self.request.GET['type']
            data = data.filter(type=type)
        if 'name' in self.request.GET:
            name = self.request.GET['name']
            data = data.filter(name=name)
        if 'day' in self.request.GET:
            day_str = self.request.GET['day']
            day = datetime.strptime(day_str, '%Y%m%d')
            data = data.filter(created__date=day)
        return data

    @action(detail=False)
    def get_btc_price(self, request, pk=None):
        headers = {'x-access-token': 'coinranking74ce3cb6b1a7eac4ce4bdd938bc524cdb3a1027a1b0fb6cd', 'User-Agent': 'Mozilla/5.0'}
        resp = requests.get('https://api.coinranking.com/v2/coin/Qwsogvtv82FCd/price', headers=headers)
        if (resp.status_code != 200):
            ServiceEvent.objects.create(device='Nuc', app=APP_SERVICE, service=ROLE_MANAGER, type=EventType.WARNING, name='requests', info='[x] error ' + str(resp.status_code) + '. ' + str(resp.content))
            ret = {'result': 'error'}
        else:
            ret = json.loads(resp.content)
        return Response(ret)
