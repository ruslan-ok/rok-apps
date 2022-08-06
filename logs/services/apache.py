from service.site_service import SiteService
from task.const import APP_LOGS, ROLE_APACHE

class ApacheLogData(SiteService):
    template_name = 'apache'

    def __init__(self, *args, **kwargs):
        super().__init__(APP_LOGS, ROLE_APACHE, local_log=True, *args, **kwargs)

