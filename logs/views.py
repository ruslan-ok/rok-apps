from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from task.const import ROLE_APACHE
from rusel.base.views import Context
from logs.config import app_config

from logs.services.apache import ApacheLogData
from logs.services.background import BackgroundLogData
from logs.services.backup_nuc_check import BackupNucCheckLogData
from logs.services.backup_nuc_full import BackupNucFullLogData
from logs.services.backup_nuc_short import BackupNucShortLogData
from logs.services.backup_vivo_check import BackupVivoCheckLogData
from logs.services.backup_v3_vivo_check import BackupV3VivoCheckLogData
from logs.services.backup_vivo_full import BackupVivoFullLogData
from logs.services.backup_vivo_short import BackupVivoShortLogData
from logs.services.backup_v3_vivo_short import BackupV3VivoShortLogData
from logs.services.intervals import IntervalsLogData
from logs.services.notification import NotificationLogData
from logs.services.overview import OverviewLogData
from logs.services.versions import VersionsLogData

class TuneData:
    def tune_dataset(self, data, group):
        return []

class LogsView(Context, TuneData):

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None
        self.request = request
        self.set_config(app_config, ROLE_APACHE)
        self.config.set_view(request)

@login_required(login_url='account:login')
def log_view(request):
    view = LogsView(request)
    context = view.get_app_context(request.user.id, icon=view.config.view_icon)
    context['log_title'] = view.config.title
    data = None
    match view.config.cur_view_group.view_id:
        case 'apache': data = ApacheLogData()
        case 'backup_nuc_check': data = BackupNucCheckLogData()
        case 'backup_nuc_full': data = BackupNucFullLogData()
        case 'backup_nuc_short': data = BackupNucShortLogData()
        case 'backup_vivo_check': data = BackupVivoCheckLogData()
        case 'backup_v3_vivo_check': data = BackupV3VivoCheckLogData()
        case 'backup_vivo_full': data = BackupVivoFullLogData()
        case 'backup_vivo_short': data = BackupVivoShortLogData()
        case 'backup_v3_vivo_short': data = BackupV3VivoShortLogData()
        case 'intervals': data = IntervalsLogData()
        case 'notification': data = NotificationLogData()
        case 'overview': data = OverviewLogData()
        case 'versions': data = VersionsLogData()
        case _: data = BackgroundLogData()
    if data:
        context.update(data.get_extra_context(request))
    template = loader.get_template(f'logs/{data.template_name}.html')
    return HttpResponse(template.render(context, request))

