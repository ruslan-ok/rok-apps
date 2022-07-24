import glob
from datetime import datetime, date, timedelta
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from task.const import ROLE_BACKUP
from rusel.base.views import Context
from backup.config import app_config
from backup.secret import *

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

class ArchItem():
    def __init__(self, mode, name, age, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = mode
        self.name = name
        self.age = age

    def __repr__(self) -> str:
        return str(self.age) + ' - ' + self.name
    
    def valid(self):
        if self.age >= self.min_range and self.age <= self.max_range:
            return 1
        return 0

class ArchList():
    def __init__(self, device, first_day, last_day, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.device = device
        self.mode = 'full'
        self.data = []
        self.first_day = first_day
        self.last_day = last_day

    def count_mode(self, day):
        if not len(self.data):
            self.mode = 'full'
            return
        arh_path_list = list(filter(lambda item: item.mode == 'full', self.data))
        arh_day = datetime.strptime(arh_path_list[0].name, self.device + '-%Y.%m.%d-full.zip').date()
        days = (day - arh_day).days
        if (days == 0) or (days >= full_duration_days):
            self.mode = 'full'
            return
        self.mode = 'short'
        return

    def get_item_by_age(self, age):
        for x in self.data:
            if x.age == age:
                return x
        return None

    def get_arh_name_by_day(self, day):
        return self.device + '-' + day.strftime('%Y.%m.%d') + '-' + self.mode + '.zip'

    def get_arh_age(self, arch, day):
        file_name = arch.replace(self.device + '-', '').replace('-full', '').replace('-short', '').replace('.zip', '')
        file_date = datetime.strptime(file_name, '%Y.%m.%d').date()
        file_days = (day - file_date).days
        return file_days

    def remove(self, name):
        for x in self.data:
            if x.name == name:
                self.data.remove(x)
                break

    def get_range(self, mode, pos):
        if mode == 'short':
            min_range = int(2**pos)-1
            max_range = int(2**(pos+1))-1
        else:
            min_range = int(10**pos)-1
            max_range = int(10**(pos+1))-1
        return min_range, max_range

    def zip_arh(self, mode_list, pos, day):
        file_age = self.get_arh_age(mode_list[pos], day)
        min_range, max_range = self.get_range(self.mode, pos)
        if file_age < min_range or file_age > max_range:
            if pos < len(mode_list)-1:
                next_file_age = self.get_arh_age(mode_list[pos+1], day)
                if next_file_age >= min_range and next_file_age <= max_range:
                    self.remove(mode_list[pos])
                    del mode_list[pos]

    def update_range(self, name, min_range, max_range):
        for x in self.data:
            if x.name == name:
                x.min_range = min_range
                x.max_range = max_range
                break

    def update_range_by_mode(self, mode):
        mode_items_list = list(filter(lambda item: item.mode == mode, self.data))
        mode_list = [x.name for x in mode_items_list]
        npp = 0
        for x in mode_list:
            min_range, max_range = self.get_range(mode, npp)
            self.update_range(x, min_range, max_range)
            npp += 1

    def fill(self):
        cur_day = self.first_day
        while cur_day <= self.last_day:
            self.count_mode(cur_day)
            arch_name = self.get_arh_name_by_day(cur_day)
            arch_age = self.get_arh_age(arch_name, self.last_day)
            item = ArchItem(self.mode, arch_name, arch_age)
            self.data.insert(0, item)
            if self.mode == 'full':
                mode_items_list = list(filter(lambda item: item.mode == 'full', self.data))
            else:
                mode_items_list = list(filter(lambda item: item.mode == 'short', self.data))
            mode_list = [x.name for x in mode_items_list]
            for y in range(2, len(mode_list)-1):
                self.zip_arh(mode_list, y, cur_day)
            cur_day = cur_day + timedelta(1)
        self.update_range_by_mode('full')
        self.update_range_by_mode('short')

    def check_name(self, name):
        for x in self.data:
            if x.name == name:
                return True
        return False

@login_required(login_url='account:login')
def backup_check(request):
    sources = []
    for src in ['Nuc', 'Vivo']:
        arch_list = ArchList(src, datetime(2022, 7, 11).date(), datetime(2022, 7, 23).date())
        arch_list.fill()
        fact_arch = [x.replace(work_dir + src.lower() + '\\', '') for x in glob.glob(work_dir + src.lower() + '\\' + '*.zip')]
        fact_arch.sort(reverse=True)
        fact_arch_info = [{'name': x, 'valid': arch_list.check_name(x)} for x in fact_arch]
        sources.append({'name': src, 'arch_data': arch_list.data, 'fact_arch': fact_arch_info})
    backup_check_view = BackupCheckView(request)
    context = backup_check_view.get_app_context(request.user.id, icon=backup_check_view.config.view_icon)
    context['sources'] = sources
    template = loader.get_template('backup/check.html')
    return HttpResponse(template.render(context, request))

"""
class Backup:

    def __init__(self, device, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.device = device
        self.mode = 'full'
        self.arh_list = []

    # Выбор режима архивирования
    def count_mode(self, day):
        if not len(self.arh_list):
            self.mode = 'full'
            return
        arh_path_list = list(filter(lambda arch: '-full' in arch, self.arh_list))
        arh_day = datetime.strptime(arh_path_list[0], self.device + '-%Y.%m.%d-full.zip').date()
        days = (day - arh_day).days
        if (days == 0) or (days >= full_duration_days):
            self.mode = 'full'
            return
        self.mode = 'short'
        return

    def add_new_arh(self, day):
        self.count_mode(day)
        self.arh_list.insert(0, self.device + '-' + day.strftime('%Y.%m.%d') + '-' + self.mode + '.zip')

    def get_arh_age(self, arh, day):
        file_name = arh.replace(self.device + '-', '').replace('-full', '').replace('-short', '').replace('.zip', '')
        file_date = datetime.strptime(file_name, '%Y.%m.%d').date()
        file_days = (day - file_date).days
        return file_days

    def zip_arh(self, mode_list, pos, day):
        file_age = self.get_arh_age(mode_list[pos], day)
        if self.mode == 'short':
            min_range = 2**(pos-1)+1
            max_range = 2**pos
        else:
            min_range = 10*(2**pos-1)+1
            max_range = 10*(2**(pos+1)-1)
        if file_age < min_range or file_age > max_range:
            if pos < len(mode_list)-1:
                next_file_age = self.get_arh_age(mode_list[pos+1], day)
                if next_file_age >= min_range and next_file_age <= max_range:
                    self.arh_list.remove(mode_list[pos])
                    del mode_list[pos]

def get_etalon():
    backup = Backup('Vivo')
    first_day = datetime(2022, 7, 11).date()
    last_day = datetime(2022, 9, 11).date() #datetime.today().date()
    cur_day = first_day
    while cur_day <= last_day:
        backup.add_new_arh(cur_day)
        mode_list = list(filter(lambda arch: backup.mode in arch, backup.arh_list))
        for y in range(2, len(mode_list)-1):
            backup.zip_arh(mode_list, y, cur_day)
        cur_day = cur_day + timedelta(1)
    return backup.arh_list

def get_arch_data():
    ret = []
    backup = Backup('Vivo')
    first_day = datetime(2022, 7, 11).date()
    last_day = datetime(2022, 7, 11).date()
    cur_day = first_day
    while cur_day <= last_day:
        backup.add_new_arh(cur_day)
        mode_list = list(filter(lambda arch: backup.mode in arch, backup.arh_list))
        for y in range(2, len(mode_list)-1):
            backup.zip_arh(mode_list, y, cur_day)
        cur_day = cur_day + timedelta(1)
    full_list = list(filter(lambda arch: 'full' in arch, backup.arh_list))
    short_list = list(filter(lambda arch: 'short' in arch, backup.arh_list))

    return ret

"""
