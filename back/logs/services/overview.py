import os
import requests, json
from datetime import date, timedelta
from logs.services.background import BackgroundLogData
from logs.service_log import ServiceLog
from task.const import APP_SERVICE, ROLE_MANAGER
from logs.models import ServiceEvent, EventType

REPORT_DEPTH_DAYS = 10


class OverviewLogData(ServiceLog):
    template_name = 'overview'

    def __init__(self):
        self.device = os.environ.get('DJANGO_DEVICE')
        super().__init__(self.device, APP_SERVICE, ROLE_MANAGER)

    def get_extra_context(self, request):
        context = {}
        context['health'] = self.get_health(REPORT_DEPTH_DAYS)
        return context

    def get_svc_descr(self, svc):
        device = svc['dev']
        if (svc['app'] == APP_SERVICE and svc['svc'] == ROLE_MANAGER):
            device = self.dev
        return ServiceLog(dev=device, app=svc['app'], svc=svc['svc'])

    def get_health(self, depth):
        this_device = os.environ.get('DJANGO_DEVICE')
        log_device = os.environ.get('DJANGO_LOG_DEVICE', 'Nuc')
        if self.use_log_api:
            svc_list = self.get_service_health_api(depth)
            svc_list += ServiceEvent.get_health(depth, app=APP_SERVICE, service=ROLE_MANAGER)
        else:
            exclude_background_svc = self.device != log_device
            svc_list = ServiceEvent.get_health(depth, exclude_background_svc=exclude_background_svc)
        services = []
        for svc in svc_list:
            if svc['app'] == APP_SERVICE and svc['dev'] != this_device:
                continue
            day_status = []
            for day_num in range(depth):
                day = date.today() - timedelta(days=day_num)
                href = day.strftime('%Y%m%d')
                if day_num == 0 and svc['app'] == APP_SERVICE:
                    bs = BackgroundLogData()
                    if not bs.get_health():
                        day_status.append({'icon': 'square-fill', 'color': 'gray', 'href': href})
                        continue
                if not svc['days'][day_num]:
                    day_status.append({'icon': 'dash', 'color': 'black', 'href': href})
                else:
                    if svc['days'][day_num] == EventType.ERROR:
                        color = 'salmon'
                    elif svc['days'][day_num] == EventType.WARNING:
                        color = '#c3955c'
                    else:
                        color = '#a3c4bb'
                    match svc['qnt'][day_num]:
                        case 0: icon = 'square-fill'
                        case 1: icon = '1-square'
                        case 2: icon = '2-square'
                        case 3: icon = '3-square'
                        case 4: icon = '4-square'
                        case 5: icon = '5-square'
                        case 6: icon = '6-square'
                        case 7: icon = '7-square'
                        case 8: icon = '8-square'
                        case 9: icon = '9-square'
                        case _: icon = 'arrow-up-right-square'
                    day_status.append({'icon': icon, 'color': color, 'href': href})
            svc_descr = self.get_svc_descr(svc)
            services.append({
                'sort': svc_descr.get_sort(),
                'icon': svc_descr.get_icon(),
                'href': svc_descr.get_href(),
                'name': svc_descr.get_descr(),
                'short_name': svc_descr.get_descr(),
                'days': day_status,
            })
        dates = [date.today() - timedelta(days=x) for x in range(depth)]
        return {'dates': dates, 'services': sorted(services, key=lambda x: x['sort'])}

    def get_service_health_api(self, depth):
        api_url = f'{self.api_host}/en/api/logs/get_service_health/?format=json&depth={depth}'
        resp = requests.get(api_url, headers=self.headers, verify=self.verify)
        if (resp.status_code != 200):
            ServiceEvent.objects.create(device=self.device, app=APP_SERVICE, service=ROLE_MANAGER, type=EventType.ERROR, name='get_remote_events', info='[x] error ' + str(resp.status_code) + '. ' + str(resp.content))
            return []
        ret = json.loads(resp.content)
        return ret
