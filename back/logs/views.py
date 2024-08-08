from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.template import loader
from logs.services.backup_check import BackupCheckLogData
from logs.services.versions import VersionsLogData
from core.views import Context
from task.const import APP_LOGS
from logs.logger import get_logger

logger = get_logger(__name__, 'logs', 'logs')

class TuneData:
    def tune_dataset(self, data, group):
        return []

class LogsView(Context, TuneData):

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None
        self.request = request
        self.set_config(APP_LOGS) # 'overview')
        self.config.set_view(request)

@login_required(login_url='account:login')
@permission_required('task.view_logs')
def log_view(request):
    view = LogsView(request)
    match view.config.cur_view_group.view_id:
        case 'backup_check': data = BackupCheckLogData()
        case 'versions': data = VersionsLogData()
    context = {}
    title = None
    if data:
        context.update(data.get_extra_context(request))
        title = context.get('title', view.config.title)
    context.update(view.get_app_context(request.user.id, icon=view.config.view_icon, title=title))
    context['log_title'] = view.config.title
    if hasattr(data, 'log_location'):
        context['log_location'] = data.log_location
    template = loader.get_template(f'logs/{data.template_name}.html')
    return HttpResponse(template.render(context, request))
