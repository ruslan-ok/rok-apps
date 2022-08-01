from logs.log_data.log_data import LogData
from task.const import APP_TODO
from task.models import ServiceEvent

class NotificationLogData(LogData):

    def get_extra_context(self):
        context = {}
        context['events'] = ServiceEvent.objects.filter(app=APP_TODO).order_by('-created')
        return context

