import os
from datetime import datetime
from service.site_service import SiteService
from backup.backup import Backup
from task.const import APP_BACKUP, ROLE_BACKUP_NUC_SHORT, ROLE_BACKUP_NUC_FULL, ROLE_BACKUP_VIVO_SHORT, ROLE_BACKUP_VIVO_FULL

class Backuper(SiteService):

    def __init__(self, device, frequency_days, *args, **kwargs):
        self.device = device
        self.frequency_days = frequency_days
        if (device == 'Nuc'):
            if (frequency_days == 1):
                self.service_name = ROLE_BACKUP_NUC_SHORT
                self.service_descr = 'Сервис "Ежедневное резервное копирование Nuc"'
            else:
                self.service_name = ROLE_BACKUP_NUC_FULL
                self.service_descr = 'Сервис "Полное резервное копирование Nuc"'
        if (device == 'Vivo'):
            if (frequency_days == 1):
                self.service_name = ROLE_BACKUP_VIVO_SHORT
                self.service_descr = 'Сервис "Ежедневное резервное копирование Vivo"'
            else:
                self.service_name = ROLE_BACKUP_VIVO_FULL
                self.service_descr = 'Сервис "Полное резервное копирование Vivo"'
        super().__init__(APP_BACKUP, self.service_name, self.service_descr, *args, **kwargs)

    def ripe(self):
        device = os.environ.get('DJANGO_BACKUP_DEVICE')
        if device != self.device:
            return False
        self.backup = Backup(device, datetime(2022, 7, 11).date(), datetime.today().date(), log_event=self.log_event)
        self.backup.fill()
        return self.backup.ripe()

    def process(self):
        self.log_event('info', 'start', self.backup.device)
        self.backup.run()
        self.log_event('info', 'stop', self.backup.device)
        return True

class BackupNucShort(Backuper):

    def __init__(self, *args, **kwargs):
        super().__init__('Nuc', 1, *args, **kwargs)

class BackupNucFull(Backuper):

    def __init__(self, *args, **kwargs):
        super().__init__('Nuc', 5, *args, **kwargs)

class BackupVivoShort(Backuper):

    def __init__(self, *args, **kwargs):
        super().__init__('Vivo', 1, *args, **kwargs)

class BackupVivoFull(Backuper):

    def __init__(self, *args, **kwargs):
        super().__init__('Vivo', 5, *args, **kwargs)

