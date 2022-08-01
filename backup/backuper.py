import os
from datetime import datetime, timedelta
from service.site_service import SiteService
from backup.backup import Backup
from task.const import APP_BACKUP

class Backuper(SiteService):

    def __init__(self, *args, **kwargs):
        super().__init__(APP_BACKUP, 'backup', *args, **kwargs)

    def ripe(self):
        device = os.environ.get('DJANGO_BACKUP_DEVICE')
        self.backup = Backup(device, datetime(2022, 7, 11).date(), datetime.today().date(), log_event=self.log_event)
        self.backup.fill()
        return self.backup.ripe()

    def process(self):
        self.log_event('info', 'start', self.backup.device)
        self.backup.run()
        ret = self.backup.last_day + timedelta(days=1)
        self.log_event('info', 'stop', self.backup.device + '. Next = ' + str(ret))
        return ret