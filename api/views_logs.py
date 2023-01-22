import requests, json, os
from datetime import datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, renderers, status

from logs.models import EventType, ServiceEvent, ServiceTask, ServiceTaskStatus
from api.serializers import LogsSerializer
from task.const import *
from family.gedcom_551.imp import import_params, import_start
from family.gedcom_551.exp import export_params, export_start
from family.views.examine import examine_params, examine_start

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

    @action(detail=False)
    def create_task(self, request):
        if 'app' not in request.GET or 'service' not in request.GET or 'item_id' not in request.GET:
            return Response({'result': 'error', 'info': "Expected parameters 'app', 'service', 'item_id'"},
                            status=status.HTTP_400_BAD_REQUEST)
        app = request.GET.get('app', 'service')
        service = request.GET.get('service', 'manager')
        item_id = request.GET.get('item_id', '')
        match (app, service):
            case ('family', 'import'): total, info = import_params(request.user, item_id)
            case ('family', 'export'): total, info = export_params(request.user, item_id)
            case ('family', 'examine'): total, info = examine_params(request.user, item_id)
            case _: total, info = None, 'Unsupported app and service'
        if total:
            task = ServiceTask.objects.create(user=request.user, app=app, service=service, item_id=item_id, status=ServiceTaskStatus.READY, done=0)
            return Response({'result': 'ok', 'task_id': task.id, 'total': total, 'info': info})
        return Response({'result': 'error', 'task_id': 0, 'total': 0, 'info': info})

    @action(detail=False)
    def start_task(self, request):
        if 'task_id' not in request.GET:
            return Response({'result': 'error', 'info': "Expected parameter 'task_id'"},
                            status=status.HTTP_400_BAD_REQUEST)
        task_id = request.GET.get('task_id', '0')
        if (task_id):
            if ServiceTask.objects.filter(id=task_id).exists():
                task = ServiceTask.objects.filter(id=task_id).get()
                try:
                    match (task.app, task.service):
                        case ('family', 'import'): ret = import_start(request.user, task.item_id, task.id)
                        case ('family', 'export'): ret = export_start(request.user, task.item_id, task.id)
                        case ('family', 'examine'): ret = examine_start(request.user, task.item_id, task.id)
                        case _: ret = {'info': 'Unsupported app and service'}
                except Exception as ex:
                    return Response({'result': 'exception', 'value': task.done, 'info': str(ex)})

                if 'status' in ret and 'info' in ret and ret['status'] == 'completed':
                    task = ServiceTask.objects.filter(id=task_id).get()
                    return Response({'result': 'ok', 'value': task.done, 'info': ret['info']})
                return Response({'result': ret['status'], 'info': ret['info']})
        return Response({'result': 'warning', 'info': f'Not found task with id {task_id}'})

    @action(detail=False)
    def get_task_status(self, request):
        if 'task_id' not in request.GET:
            return Response({'result': 'error', 'info': "Expected parameter 'task_id'"},
                            status=status.HTTP_400_BAD_REQUEST)
        task_id = request.GET.get('task_id', '0')
        if (task_id):
            if ServiceTask.objects.filter(id=task_id).exists():
                task = ServiceTask.objects.filter(id=task_id).get()
                return Response({'result': 'ok', 'value': task.done})
        return Response({'result': 'error', 'info': f'Not found task with id {task_id}'})
