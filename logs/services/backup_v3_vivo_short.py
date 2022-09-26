from service.site_service import SiteService
from task.const import APP_BACKUP, ROLE_BACKUP_V3_SHORT

class BackupV3VivoShortLogData(SiteService):

    def __init__(self, *args, **kwargs):
        super().__init__(APP_BACKUP, ROLE_BACKUP_V3_SHORT, device='Vivo', *args, **kwargs)

