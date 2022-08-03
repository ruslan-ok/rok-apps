from logs.log_data.log_data import LogData
from task.const import APP_BACKUP
from task.models import ServiceEvent

class BackupLogData(LogData):

    def get_extra_context(self):
        context = {}
        context['events'] = ServiceEvent.objects.filter(app=APP_BACKUP).order_by('-created')
        return context

