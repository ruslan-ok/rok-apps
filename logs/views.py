from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from task.const import ROLE_LOGS
from rusel.base.views import Context
from logs.config import app_config

from logs.log_data.apache import ApacheLogData
from logs.log_data.background import BackgroundLogData
from logs.log_data.backup import BackupLogData
from logs.log_data.backup_check import BackupCheckLogData
from logs.log_data.intervals import IntervalsLogData
from logs.log_data.notification import NotificationLogData
from logs.log_data.versions import VersionsLogData

class TuneData:
    def tune_dataset(self, data, group):
        return []

class LogsView(Context, TuneData):

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None
        self.request = request
        self.set_config(app_config, ROLE_LOGS)
        self.config.set_view(request)

@login_required(login_url='account:login')
def log_view(request):
    view = LogsView(request)
    context = view.get_app_context(request.user.id, icon=view.config.view_icon)
    context['log_title'] = view.config.title
    data = None
    match view.config.cur_view_group.view_id:
        case 'backup': data = BackupLogData()
        case 'backup_check': data = BackupCheckLogData()
        case 'apache': data = ApacheLogData()
        case 'notification': data = NotificationLogData()
        case 'intervals': data = IntervalsLogData()
        case 'versions': data = VersionsLogData()
        case _: data = BackgroundLogData()
    if data:
        context.update(data.get_extra_context())
    template = loader.get_template(f'logs/{view.config.cur_view_group.view_id}.html')
    return HttpResponse(template.render(context, request))

