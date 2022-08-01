from logs.log_data.log_data import LogData
from task.const import APP_LOGS
from task.models import ServiceEvent

class ApacheLogData(LogData):

    def get_extra_context(self):
        context = {}
        context['events'] = ServiceEvent.objects.filter(app=APP_LOGS).order_by('-created')
        return context

