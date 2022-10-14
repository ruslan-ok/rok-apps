from datetime import datetime
from backup.backup_v3 import Backup_v3

class BackupV3CheckLogData():
    template_name = 'backup_v3_check'

    def __init__(self, dev):
        self.dev = dev

    def get_extra_context(self, request):
        start = datetime(2022, 9, 22).date()
        stop  = datetime.today().date()
        backup = Backup_v3(
            device=self.dev, 
            service_name='Ежедневный бэкап', 
            duration=1, 
            folders=[], 
            first_day=start, 
            last_day=stop, 
            log_event=None)
        context = {}
        context['etalon'] = backup.etalon
        context['fact'] = backup.fact
        return context

