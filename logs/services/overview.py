import os
import requests, json
from datetime import date, timedelta
from logs.services.background import BackgroundLogData
from service.site_service import SiteService
from task.const import APP_BACKUP, APP_FUEL, APP_LOGS, APP_SERVICE, APP_TODO, ROLE_APACHE, ROLE_BACKUP_FULL, ROLE_BACKUP_SHORT, ROLE_MANAGER, ROLE_NOTIFICATOR, ROLE_PART
from logs.models import ServiceEvent, EventType

REPORT_DEPTH_DAYS = 10

SERVICES = [
    (1, 'SM', '???',  APP_SERVICE, ROLE_MANAGER,      'fast-forward',  'background',           'Service manager'),
    (2, 'NS', 'Nuc',  APP_BACKUP,  ROLE_BACKUP_SHORT, 'save',          'backup_nuc_short',     'Backup Nuc short'),
    (3, 'NF', 'Nuc',  APP_BACKUP,  ROLE_BACKUP_FULL,  'save-fill',     'backup_nuc_full',      'Backup Nuc full'),
    (4, 'VS', 'Vivo', APP_BACKUP,  ROLE_BACKUP_SHORT, 'save',          'backup_vivo_short',    'Backup Vivo short'),
    (5, 'VF', 'Vivo', APP_BACKUP,  ROLE_BACKUP_FULL,  'save-fill',     'backup_vivo_full',     'Backup Vivo full'),
    (6, 'TN', 'Nuc',  APP_TODO,    ROLE_NOTIFICATOR,  'bell',          'notification',         'Task Notificator'),
    (7, 'SI', 'Nuc',  APP_FUEL,    ROLE_PART,         'tools',         'intervals',            'Service intervals'),
    (8, 'AL', 'Nuc',  APP_LOGS,    ROLE_APACHE,       'server',        'apache',               'Apache log'),
]

class OverviewLogData(SiteService):
    template_name = 'overview'

    def __init__(self):
        super().__init__(APP_SERVICE, ROLE_MANAGER)

    def get_extra_context(self, request):
        context = {}
        context['health'] = self.get_health(REPORT_DEPTH_DAYS)
        return context

    def get_svc_descr(self, svc):
        for service in SERVICES:
            device = service[2]
            if service[1] == 'SM':
                device = os.environ.get('DJANGO_DEVICE')
            if svc['dev'] == device and svc['app'] == service[3] and svc['svc'] == service[4]:
                return {'icon': service[5], 'href': service[6], 'name': service[7], 'sort': service[0]}
        return None

    def get_health(self, depth):
        this_device = os.environ.get('DJANGO_DEVICE')
        if self.use_log_api:
            svc_list = self.get_service_health_api(depth)
            svc_list += ServiceEvent.get_health(depth, app=APP_SERVICE, service=ROLE_MANAGER)
        else:
            svc_list = ServiceEvent.get_health(depth)
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
                        day_status.append({'icon': 'circle-fill', 'color': 'gray', 'href': href})
                        continue
                if not svc['days'][day_num]:
                    day_status.append({'icon': 'dash', 'color': 'black', 'href': href})
                else:
                    if svc['days'][day_num] == EventType.ERROR:
                        color = 'red'
                    elif svc['days'][day_num] == EventType.WARNING:
                        color = 'orange'
                    else:
                        color = 'green'
                    match svc['qnt'][day_num]:
                        case 0: icon = 'circle-fill'
                        case 1: icon = '1-circle'
                        case 2: icon = '2-circle'
                        case 3: icon = '3-circle'
                        case 4: icon = '4-circle'
                        case 5: icon = '5-circle'
                        case 6: icon = '6-circle'
                        case 7: icon = '7-circle'
                        case 8: icon = '8-circle'
                        case 9: icon = '9-circle'
                        case _: icon = 'arrow-up-right-circle'
                    day_status.append({'icon': icon, 'color': color, 'href': href})
            svc_descr = self.get_svc_descr(svc)
            if not svc_descr:
                services.append({
                    'sort': 99,
                    'icon': None,
                    'href': None,
                    'name': svc['dev'] + ':' + svc['app'] + ':' + svc['svc'],
                    'days': day_status,
                })
            else:
                services.append({
                    'sort': svc_descr['sort'],
                    'icon': svc_descr['icon'],
                    'href': svc_descr['href'],
                    'name': svc_descr['name'],
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
