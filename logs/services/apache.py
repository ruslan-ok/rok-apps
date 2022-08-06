from service.site_service import SiteService
from task.const import APP_LOGS, ROLE_APACHE
from logs.site_stat import get_site_stat

class ApacheLogData(SiteService):
    template_name = 'apache'

    def __init__(self, *args, **kwargs):
        super().__init__(APP_LOGS, ROLE_APACHE, local_log=True, *args, **kwargs)

    def get_extra_context(self, request):
        context = super().get_extra_context(request)
        statistics = get_site_stat(request.user)
        indicators = statistics[0]
        stat = statistics[1]
        context['indicators'] = indicators
        context['show_stat'] = (len(stat) > 0)
        context['stat'] = stat
        return context