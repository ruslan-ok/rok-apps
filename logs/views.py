from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from logs.services.apache import ApacheLogData
from logs.services.background import BackgroundLogData
from logs.services.backup_check import BackupCheckLogData
from logs.services.overview import OverviewLogData
from logs.services.versions import VersionsLogData
from logs.service_log import ServiceLog
from rusel.base.views import Context
from logs.config import app_config
from task import const

class TuneData:
    def tune_dataset(self, data, group):
        return []

class LogsView(Context, TuneData):

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None
        self.request = request
        self.set_config(app_config, 'overview')
        self.config.set_view(request)

@login_required(login_url='account:login')
def log_view(request):
    view = LogsView(request)
    context = view.get_app_context(request.user.id, icon=view.config.view_icon)
    context['log_title'] = view.config.title
    dev = None
    if 'dev' in request.GET:
        dev = request.GET.get('dev')
    app = None
    if 'app' in request.GET:
        app = request.GET.get('app')
    svc = None
    if 'svc' in request.GET:
        svc = request.GET.get('svc')
    match view.config.cur_view_group.view_id:
        case 'backup_check': data = BackupCheckLogData()
        case 'versions': data = VersionsLogData()
        case _:
            match (app, svc):
                case (None, None): data = OverviewLogData()
                case (const.APP_SERVICE, const.ROLE_MANAGER): data = BackgroundLogData()
                case (const.APP_LOGS, const.ROLE_APACHE): data = ApacheLogData()
                case _: data = ServiceLog(dev=dev, app=app, svc=svc)
    if data:
        context.update(data.get_extra_context(request))
    template = loader.get_template(f'logs/{data.template_name}.html')
    return HttpResponse(template.render(context, request))

