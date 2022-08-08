from service.site_service import SiteService
from task.const import APP_BACKUP, ROLE_BACKUP_SHORT

class BackupNucShortLogData(SiteService):

    def __init__(self, *args, **kwargs):
        super().__init__(APP_BACKUP, ROLE_BACKUP_SHORT, device='Nuc', *args, **kwargs)

