from logs.models import EventType
from service.site_service import SiteService
from backup.backup import Backup
from task.const import APP_BACKUP, ROLE_BACKUP_SHORT, ROLE_BACKUP_FULL

class Backuper(SiteService):

    def __init__(self, service_task, *args, **kwargs):
        self.frequency_days = service_task.repeat_num
        if self.frequency_days == 1:
            service_name = ROLE_BACKUP_SHORT
        else:
            service_name = ROLE_BACKUP_FULL
        self.folders = service_task.info
        super().__init__(APP_BACKUP, service_name, service_task.name, *args, **kwargs)

    def ripe(self):
        self.backup = Backup(self.device, log_event=self.log_event)
        ret = self.backup.ripe()
        return ret

    def process(self):
        self.log_event(EventType.INFO, 'start', self.backup.device)
        self.backup.run(self.folders)
        self.log_event(EventType.INFO, 'stop', self.backup.device)
        return True
