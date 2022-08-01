import os, glob
from datetime import datetime
from logs.log_data.log_data import LogData
from task.const import APP_BACKUP
from task.models import ServiceEvent
from backup.backup import Backup

class BackupLogData(LogData):

    def get_extra_context(self):
        context = {}
        context['events'] = ServiceEvent.objects.filter(app=APP_BACKUP).order_by('-created')
        sources = []
        for src in ['Nuc', 'Vivo']:
            arch_list = Backup(src, datetime(2022, 7, 11).date(), datetime.today().date())
            arch_list.fill()
            backup_folder = os.environ.get('DJANGO_BACKUP_FOLDER')
            fact_arch = [x.replace(backup_folder + src.lower() + '\\', '') for x in glob.glob(backup_folder + src.lower() + '\\' + '*.zip')]
            fact_arch.sort(reverse=True)
            fact_arch_info = [{'name': x, 'valid': arch_list.check_name(x)} for x in fact_arch]
            sources.append({'name': src, 'arch_data': arch_list.data, 'fact_arch': fact_arch_info})
        context['sources'] = sources
        return context

