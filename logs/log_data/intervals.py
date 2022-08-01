from logs.log_data.log_data import LogData
from task.const import APP_FUEL
from task.models import ServiceEvent

class IntervalsLogData(LogData):

    def get_extra_context(self):
        context = {}
        context['events'] = ServiceEvent.objects.filter(app=APP_FUEL).order_by('-created')
        return context

