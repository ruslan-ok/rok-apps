from datetime import date, timedelta
from logs.models import ServiceEvent
from service.site_service import SiteService
from task.const import APP_LOGS, APP_TODO

REPORT_DEPTH_DAYS = 5

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
        super().__init__('service', 'manager', *args, **kwargs)

    def get_extra_context(self, request):
        context = {}
        dates = [date.today() - timedelta(days=x) for x in range(REPORT_DEPTH_DAYS)]
        context['dates'] = dates
        services = []
        for service in SERVICES:
            days = []
            match service[0]:
                case 'SM': days = self.get_service_health('service', 'manager')
                case 'NF': days = self.get_service_health('backup', 'nuc_full')
                case 'NS': days = self.get_service_health('backup', 'nuc_short')
                case 'VF': days = self.get_service_health('backup', 'vivo_full')
                case 'VS': days = self.get_service_health('backup', 'vivo_short')
                case 'TN': days = self.get_service_health('todo', 'notificator')
                case 'SI': days = self.get_service_health('fuel', 'serv_interval')
                case 'AL': days = self.get_service_health('logs', 'apache')
                case _: days = [{'icon': 'dash-circle-dotted', 'color': 'gray'} for x in range(REPORT_DEPTH_DAYS)]
            services.append({
                'icon': service[1],
                'href': service[2],
                'name': service[3],
                'days': days,
            })
        context['services'] = services
        return context

    def get_service_health(self, app, service):
        ret = []
        for day_num in range(REPORT_DEPTH_DAYS):
            day = date.today() - timedelta(days=day_num)
            href = day.strftime('%Y%m%d')
            events = self.get_events(app=app, service=service, day=day, local_log=(app == 'service' or app == APP_LOGS))
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
                if app == APP_TODO and service == 'notificator':
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

