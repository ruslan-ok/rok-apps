from django.conf import settings
from logs.service_log import ServiceLog
from logs.site_stat import get_site_stat

class ApacheLogData(ServiceLog):
    template_name = 'apache'

    def __init__(self):
        log_device = settings.DJANGO_LOG_DEVICE
        super().__init__(log_device, 'logs', 'apache')

    def get_extra_context(self, request):
        context = super().get_extra_context(request)
        statistics = get_site_stat(request.user)
        indicators = statistics[0]
        stat = statistics[1]
        context['indicators'] = indicators
        context['show_stat'] = (len(stat) > 0)
        context['stat'] = stat
        return context