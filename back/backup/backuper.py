import os
from datetime import datetime
from service.site_service import SiteService
from backup.backup import Backup
from task.const import ROLE_BACKUP_SHORT, ROLE_BACKUP_FULL
from logs.logger import Logger


logger = Logger(__name__)

class Backuper(SiteService):

    def __init__(self, service_task, *args, **kwargs):
        start = datetime(2022, 10, 15).date()
        stop  = datetime.today().date()
        duration = 1
        folders = []
        self.backup = None
        service_name = ROLE_BACKUP_SHORT
        params = service_task.info.split('\r\n')
        if len(params):
            if 'duration:' in params[0]:
                duration = int(params[0].replace('duration:', ''))
            folders = params[1:]
        if not len(folders):
            logger.warning('params: empty folders list')
        else:
            if duration != 1:
                service_name = ROLE_BACKUP_FULL
            self.backup = Backup(
                os.environ.get('DJANGO_DEVICE'),
                service_name=service_name,
                service_descr=service_task.name,
                duration=duration,
                folders=folders,
                first_day=start,
                last_day=stop,
            )
        super().__init__(service_task.name, *args, **kwargs)

    def ripe(self):
        ret = False
        if self.backup:
            ret = self.backup.ripe()
        return ret, True

    def process(self):
        self.backup.run()
        return True
