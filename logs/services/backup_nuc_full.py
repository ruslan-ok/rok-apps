from service.site_service import SiteService
from task.const import APP_BACKUP, ROLE_BACKUP_FULL

class BackupNucFullLogData(SiteService):

    def __init__(self, *args, **kwargs):
        super().__init__(APP_BACKUP, ROLE_BACKUP_FULL, device='Nuc', local_log=True, *args, **kwargs)

