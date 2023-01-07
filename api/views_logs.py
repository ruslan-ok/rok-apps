import requests, json, os
from datetime import datetime, timedelta
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, renderers, status

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
        api_url = os.getenv('API_COIN_RATE')
        api_key = os.getenv('API_COIN_RATE_KEY')
        if not api_url or not api_key:
            info = 'Not specified variables API_COIN_RATE and/or API_COIN_RATE_KEY.'
            ServiceEvent.objects.create(device='Nuc', app=APP_SERVICE, service=ROLE_MANAGER, type=EventType.WARNING, name='os.getenv', info=info)
            ret = {'result': 'warning', 'info': info}
            return Response(ret)
        else:
            headers = {'x-access-token': api_key, 'User-Agent': 'Mozilla/5.0'}
            resp = requests.get(api_url + 'price', headers=headers)
            if (resp.status_code != 200):
                info = 'Failed call for BTC price. Status = ' + str(resp.status_code) + '. ' + str(resp.content)
                ServiceEvent.objects.create(device='Nuc', app=APP_SERVICE, service=ROLE_MANAGER, type=EventType.WARNING, name='requests', info=info)
                ret = {'result': 'warning', 'info': info}
            else:
                ret = json.loads(resp.content)
            return Response(ret)

    @action(detail=False)
    def get_service_health(self, request, pk=None):
        depth = 3
        if 'depth' in request.GET:
            depth = int(request.GET['depth'])
        ret = ServiceEvent.get_health(depth)
        return Response(ret)

    @action(detail=False)
    def write_event(self, request, pk=None):
        if 'device' not in request.GET or 'app' not in request.GET or 'service' not in request.GET or \
            'type' not in request.GET or 'name' not in request.GET or 'info' not in request.GET:
            return Response({'result': 'error', 'info': "Expected parameters 'device', 'app', 'service', 'type', 'name' and 'info'"},
                            status=status.HTTP_400_BAD_REQUEST)
        device = request.GET.get('device', 'nuc')
        app = request.GET.get('app', 'service')
        service = request.GET.get('service', 'manager')
        type = request.GET.get('type', 'info')
        name = request.GET.get('name', 'unknown')
        info = request.GET.get('info', 'undefined')
        ServiceEvent.objects.create(device=device, app=app, service=service, type=type, name=name, info=info)
        return Response({'result': 'ok'})
