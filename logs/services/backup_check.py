from backup.backup import Backup

class BackupCheckLogData():
    template_name = 'backup_check'

    def __init__(self, dev):
        self.dev = dev

    def get_extra_context(self, request):
        context = {}
        backup = Backup(self.dev)
        backup.fill()
        context['etalon'] = backup.etalon
        context['fact'] = backup.fact
        return context

