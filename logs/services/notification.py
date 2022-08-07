from service.site_service import SiteService
from task.const import APP_TODO

class NotificationLogData(SiteService):

    def __init__(self, *args, **kwargs):
        super().__init__(APP_TODO, 'notificator', *args, **kwargs)

