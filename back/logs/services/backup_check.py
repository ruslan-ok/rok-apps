from datetime import datetime
import os
from backup.backup import Backup

SERVICE_NAME_1 = 'Ежедневный бэкап'
SERVICE_NAME_7 = 'Еженедельный бэкап'

class BackupCheckLogData():
    template_name = 'backup_check'

    def __init__(self):
        self.dev = os.environ.get('DJANGO_DEVICE')

    def get_extra_context(self, request):
        start = datetime(2022, 10, 15).date()
        stop  = datetime.today().date()
        backup_1 = Backup(
            device=self.dev, 
            service_name=SERVICE_NAME_1, 
            duration=1, 
            folders=[], 
            first_day=start, 
            last_day=stop, 
            log_event=None)
        backup_7 = Backup(
            device=self.dev, 
            service_name=SERVICE_NAME_7,
            duration=7,
            folders=[], 
            first_day=start, 
            last_day=stop, 
            log_event=None)
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

