import os, json
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.template import loader
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from logs.services.apache import ApacheLogData
from logs.services.background import BackgroundLogData
from logs.services.backup_check import BackupCheckLogData
from logs.services.overview import OverviewLogData
from logs.services.versions import VersionsLogData
from logs.service_log import ServiceLog
from core.views import Context
from core.context import AppContext
from logs.config import app_config
from logs.models import ServiceEvent
from task.const import APP_LOGS, ROLE_APACHE

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
@permission_required('task.view_logs')
def log_view(request):
    view = LogsView(request)
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
                case ('cron', 'worker'): data = BackgroundLogData()
                case ('logs', 'apache'): data = ApacheLogData()
                case _: data = ServiceLog(dev=dev, app=app, svc=svc)
    context = {}
    title = None
    if data:
        context.update(data.get_extra_context(request))
        title = context.get('title', view.config.title)
    context.update(view.get_app_context(request.user.id, icon=view.config.view_icon, title=title))
    context['log_title'] = view.config.title
    context['log_location'] = data.log_location
    template = loader.get_template(f'logs/{data.template_name}.html')
    return HttpResponse(template.render(context, request))

class LogEventView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = "logs/event.html"
    permission_required = 'task.view_logs'

    def get_context_data(self, **kwargs):
        def dict_to_list(dict_value: dict) -> list:
            ret = []
            for key, value in dict_value.items():
                if type(value) != dict:
                    if key == 'name' and value == '----':
                        continue
                    if value is None:
                        continue
                    ret.append({'name': key, 'value': value})
                else:
                    ret += dict_to_list(value)
            return ret

        app_context = AppContext(self.request.user, APP_LOGS, ROLE_APACHE)
        context = app_context.get_context()
        context['hide_add_item_input'] = True
        location = self.kwargs.get('location')
        pk = int(self.kwargs.get('pk'))
        event_fields = []
        if location == os.environ.get('DJANGO_DEVICE', ''):
            service_event = ServiceEvent.objects.filter(id=pk).get()
            event_dict = {}
            for field in service_event._meta.get_fields():
                name = field.name
                value = getattr(service_event, field.name)
                if name == 'details':
                    try:
                        value = json.loads(value)
                    except:
                        pass
                if name == 'info':
                    try:
                        value = json.loads(value)
                        continue
                    except:
                        pass
                event_dict[name] = value
            event_fields = dict_to_list(event_dict)
        else:
            pass
        context['event_fields'] = event_fields
        return context