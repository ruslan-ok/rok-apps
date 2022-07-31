import os, glob
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from task.const import ROLE_BACKUP
from rusel.base.views import Context
from backup.config import app_config
from backup.backup import Backup

class TuneData:
    def tune_dataset(self, data, group):
        return []

class BackupCheckView(Context, TuneData):
    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None
        self.request = request
        self.set_config(app_config, ROLE_BACKUP)
        self.config.set_view(request)

@login_required(login_url='account:login')
def backup_check(request):
    sources = []
    for src in ['Nuc', 'Vivo']:
        arch_list = Backup(src, datetime(2022, 7, 11).date(), datetime.today().date())
        arch_list.fill()
        backup_folder = os.environ.get('DJANGO_BACKUP_FOLDER')
        fact_arch = [x.replace(backup_folder + src.lower() + '\\', '') for x in glob.glob(backup_folder + src.lower() + '\\' + '*.zip')]
        fact_arch.sort(reverse=True)
        fact_arch_info = [{'name': x, 'valid': arch_list.check_name(x)} for x in fact_arch]
        sources.append({'name': src, 'arch_data': arch_list.data, 'fact_arch': fact_arch_info})
    backup_check_view = BackupCheckView(request)
    context = backup_check_view.get_app_context(request.user.id, icon=backup_check_view.config.view_icon)
    context['sources'] = sources
    template = loader.get_template('backup/check.html')
    return HttpResponse(template.render(context, request))
