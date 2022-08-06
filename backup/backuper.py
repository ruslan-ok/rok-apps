import os
from datetime import datetime
from logs.models import EventType
from service.site_service import SiteService
from backup.backup import Backup
from task.const import APP_BACKUP, ROLE_BACKUP_NUC_SHORT, ROLE_BACKUP_NUC_FULL, ROLE_BACKUP_VIVO_SHORT, ROLE_BACKUP_VIVO_FULL
from logs.models import ServiceEvent

class Backuper(SiteService):

    def __init__(self, device, frequency_days, *args, **kwargs):
        self.backup_device = device
        self.frequency_days = frequency_days
        if (device == 'Nuc'):
            local_log = True
            if (frequency_days == 1):
                self.service_name = ROLE_BACKUP_NUC_SHORT
                self.service_descr = 'Сервис "Ежедневное резервное копирование Nuc"'
            else:
                self.service_name = ROLE_BACKUP_NUC_FULL
                self.service_descr = 'Сервис "Полное резервное копирование Nuc"'
        if (device == 'Vivo'):
            local_log = False
            if (frequency_days == 1):
                self.service_name = ROLE_BACKUP_VIVO_SHORT
                self.service_descr = 'Сервис "Ежедневное резервное копирование Vivo"'
            else:
                self.service_name = ROLE_BACKUP_VIVO_FULL
                self.service_descr = 'Сервис "Полное резервное копирование Vivo"'
        super().__init__(APP_BACKUP, self.service_name, self.service_descr, local_log=local_log, *args, **kwargs)
        ServiceEvent.objects.create(device=self.device, app='service', service='manager', type=EventType.DEBUG, name='init', info='Backuper')

    def ripe(self):
        ServiceEvent.objects.create(device=self.device, app='service', service='manager', type=EventType.DEBUG, 
            name='method', info=f'+ripe(): self.device={str(self.device)}, self.backup_device={str(self.backup_device)}')
        if self.device != self.backup_device:
            ServiceEvent.objects.create(device=self.device, app='service', service='manager', type=EventType.DEBUG, name='method', info='-ripe(): False')
            return False
        self.backup = Backup(self.device, datetime(2022, 7, 11).date(), datetime.today().date(), log_event=self.log_event)
        self.backup.fill()
        ret = self.backup.ripe()
        ServiceEvent.objects.create(device=self.device, app='service', service='manager', type=EventType.DEBUG, name='method', info=f'-ripe(): {str(ret)}')
        return ret
        
    def process(self):
        self.log_event(EventType.INFO, 'start', self.backup.device)
        self.backup.run()
        self.log_event(EventType.INFO, 'stop', self.backup.device)
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

