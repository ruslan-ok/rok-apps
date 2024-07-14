from datetime import datetime
from django.conf import settings
from backup.backup import Backup

SERVICE_NAME_1 = 'daily'
SERVICE_NAME_7 = 'weekly'

class BackupCheckLogData():
    template_name = 'backup_check'

    def __init__(self):
        self.dev = settings.DJANGO_DEVICE

    def get_extra_context(self, request):
        start = datetime(2022, 10, 15).date()
        stop  = datetime.today().date()
        backup_1 = Backup(
            device=self.dev, 
            service_name=SERVICE_NAME_1, 
            service_descr='daily',
            duration=1, 
            folders=[], 
            first_day=start, 
            last_day=stop)
        backup_7 = Backup(
            device=self.dev, 
            service_name=SERVICE_NAME_7,
            service_descr='weekly',
            duration=7,
            folders=[], 
            first_day=start, 
            last_day=stop)
        context = {}
        context['backup_deeps'] = [
            {
                'device': backup_1.device,
                'periodicity': backup_1.duration,
                'service_name': backup_1.service_name,
                'etalon': backup_1.etalon,
                'fact': backup_1.fact
            },
            {
                'device': backup_7.device,
                'periodicity': backup_7.duration,
                'service_name': backup_7.service_name,
                'etalon': backup_7.etalon,
                'fact': backup_7.fact
            },
            ]
        return context

