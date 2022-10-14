import json
from datetime import datetime
from logs.models import EventType
from service.site_service import SiteService
from backup.backup import Backup
from task.const import APP_BACKUP, ROLE_BACKUP_SHORT, ROLE_BACKUP_FULL

class Backuper(SiteService):

    def __init__(self, service_task):
        start = datetime(2022, 10, 15).date()
        stop  = datetime.today().date()
        duration = 1
        folders = []
        self.backup = None
        service_name = ROLE_BACKUP_SHORT
        str_params = service_task.info
        if str_params:
            params = json.loads(str_params)
            if 'duration' in params:
                duration = params['duration']
            if 'folders' in params:
                folders = params['folders']
        if not len(folders):
            self.log_event(EventType.WARNING, 'params', 'empty folders list')
            super().__init__(APP_BACKUP, service_name, service_task.name)
        else:
            if duration != 1:
                service_name = ROLE_BACKUP_FULL
            super().__init__(APP_BACKUP, service_name, service_task.name)
            self.backup = Backup(self.device, service_name=service_task.name, duration=duration, folders=folders, first_day=start, last_day=stop, log_event=self.log_event)

    def ripe(self):
        ret = False
        if self.backup:
            ret = self.backup.ripe()
        return ret

    def process(self):
        self.log_event(EventType.INFO, 'start', self.backup.device)
        self.backup.run()
        self.log_event(EventType.INFO, 'stop', self.backup.device)
        return True
