import json
from datetime import datetime
from logs.models import EventType
from service.site_service import SiteService
from backup.backup_v3 import Backup_v3
from task.const import APP_BACKUP, ROLE_BACKUP_V3_SHORT, ROLE_BACKUP_CUSTOM

class Backuper_v3(SiteService):

    def __init__(self, service_task):
        start = datetime(2022, 9, 22).date()
        stop  = datetime.today().date()
        duration = 1
        folders = []
        self.backup = None
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
            if duration == 1:
                service_name = ROLE_BACKUP_V3_SHORT
            super().__init__(APP_BACKUP, service_name, service_task.name)
            self.backup = Backup_v3(self.device, service_name=service_task.name, duration=duration, folders=folders, first_day=start, last_day=stop, log_event=self.log_event)

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
