from service.site_service import SiteService
from task.const import APP_FUEL, ROLE_PART

class IntervalsLogData(SiteService):

    def __init__(self, *args, **kwargs):
        super().__init__(APP_FUEL, ROLE_PART, *args, **kwargs)

