import os
from datetime import date, timedelta
from logs.services.background import BackgroundLogData
from service.site_service import SiteService
from task.const import APP_BACKUP, APP_FUEL, APP_LOGS, APP_SERVICE, APP_TODO, ROLE_APACHE, ROLE_BACKUP_FULL, ROLE_BACKUP_SHORT, ROLE_MANAGER, ROLE_NOTIFICATOR, ROLE_PART

REPORT_DEPTH_DAYS = 10

SERVICES = [
    ('SM', 'fast-forward',  'background',           'Service manager'),
    ('NS', 'save',          'backup_nuc_short',     'Backup Nuc short'),
    ('NF', 'save-fill',     'backup_nuc_full',      'Backup Nuc full'),
    ('VS', 'save',          'backup_vivo_short',    'Backup Vivo short'),
    ('VF', 'save-fill',     'backup_vivo_full',     'Backup Vivo full'),
    ('TN', 'bell',          'notification',         'Task Notificator'),
    ('SI', 'tools',         'intervals',            'Service intervals'),
    ('AL', 'server',        'apache',               'Apache log'),
]

class OverviewLogData(SiteService):
    template_name = 'overview'

    def __init__(self, *args, **kwargs):
        super().__init__(APP_SERVICE, ROLE_MANAGER, *args, **kwargs)

    def get_extra_context(self, request):
        context = {}
        context['health'] = self.get_health(REPORT_DEPTH_DAYS)
        return context

    def get_health(self, depth):
        dates = [date.today() - timedelta(days=x) for x in range(depth)]
        this_device = os.environ.get('DJANGO_DEVICE')
        services = []
        for service in SERVICES:
            days = []
            match service[0]:
                case 'SM': days = self.get_service_health(this_device, APP_SERVICE, ROLE_MANAGER, depth)
                case 'NF': days = self.get_service_health('Nuc', APP_BACKUP, ROLE_BACKUP_FULL, depth)
                case 'NS': days = self.get_service_health('Nuc', APP_BACKUP, ROLE_BACKUP_SHORT, depth)
                case 'VF': days = self.get_service_health('Vivo', APP_BACKUP, ROLE_BACKUP_FULL, depth)
                case 'VS': days = self.get_service_health('Vivo', APP_BACKUP, ROLE_BACKUP_SHORT, depth)
                case 'TN': days = self.get_service_health('Nuc', APP_TODO, ROLE_NOTIFICATOR, depth)
                case 'SI': days = self.get_service_health('Nuc', APP_FUEL, ROLE_PART, depth)
                case 'AL': days = self.get_service_health('Nuc', APP_LOGS, ROLE_APACHE, depth)
                case _: days = [{'icon': 'dash-circle-dotted', 'color': 'gray'} for x in range(depth)]
            services.append({
                'icon': service[1],
                'href': service[2],
                'name': service[3],
                'days': days,
            })
        return {'dates': dates, 'services': services}

    def get_service_health(self, device, app, service, depth):
        ret = []
        for day_num in range(depth):
            day = date.today() - timedelta(days=day_num)
            href = day.strftime('%Y%m%d')
            if day_num == 0 and app == APP_SERVICE:
                bs = BackgroundLogData()
                if not bs.get_health():
                    ret.append({'icon': 'circle-fill', 'color': 'gray', 'href': href})
                    continue
            events = self.get_events(device=device, app=app, service=service, day=day, local_log=(app == APP_SERVICE))
            if not len(events):
                ret.append({'icon': 'dash', 'color': 'black', 'href': href})
                continue
            has_error = False
            has_warn = False
            qnt = 0
            for event in events:
                if event.type == 'error':
                    has_error = True
                if event.type == 'warning':
                    has_warn = True
                if app == APP_TODO and service == ROLE_NOTIFICATOR:
                    if event.name == 'process' and 'task qnt = ' in event.info:
                        add_qnt = int(event.info.split('task qnt = ')[1])
                        qnt += add_qnt
            if has_error:
                color = 'red'
            elif has_warn:
                color = 'orange'
            else:
                color = 'green'
            match qnt:
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
            ret.append({'icon': icon, 'color': color, 'href': href})
        return ret

