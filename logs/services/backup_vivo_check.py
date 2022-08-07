import os, glob
from datetime import datetime
from backup.backup import Backup

class BackupVivoCheckLogData():
    template_name = 'backup_check'

    def get_extra_context(self, request):
        context = {}
        backup = Backup('Vivo')
        backup.fill()
        context['etalon'] = backup.etalon
        context['fact'] = backup.fact
        return context

