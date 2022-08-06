import os, glob
from datetime import datetime
from backup.backup import Backup

class BackupVivoCheckLogData():
    template_name = 'backup_check'

    def get_extra_context(self, request):
        context = {}
        sources = []
        src = 'Vivo'
        arch_list = Backup(src, datetime(2022, 7, 11).date(), datetime.today().date())
        arch_list.fill()
        backup_folder = os.environ.get('DJANGO_BACKUP_FOLDER')
        fact_arch = [x.replace(backup_folder + src.lower() + '\\', '') for x in glob.glob(backup_folder + src.lower() + '\\' + '*.zip')]
        fact_arch.sort(reverse=True)
        fact_arch_info = [{'name': x, 'valid': arch_list.check_name(x)} for x in fact_arch]
        sources.append({'name': src, 'arch_data': arch_list.data, 'fact_arch': fact_arch_info})
        context['sources'] = sources
        return context

