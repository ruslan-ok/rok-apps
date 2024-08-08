from pathlib import Path
from datetime import datetime, timedelta
from django.conf import settings


class ArchItem():
    def __init__(self, is_etalon, name, age, size=None):
        super().__init__()
        self.is_etalon = is_etalon
        self.name = name
        self.age = age
        self.min_range = None
        self.max_range = None
        self.size = size
        self.etalon = None
        self.facts = []

    def __repr__(self) -> str:
        valid = 1 if self.age >= self.min_range and self.age <= self.max_range else 0
        return f'{valid}: [{self.min_range}-{self.max_range}] - {self.age} - {self.name}'
    
    def __str__(self):
        return self.__repr__()
    
    def ripe(self):
        if self.age >= self.min_range and self.age <= self.max_range:
            return 1
        return 0
    
    def state_class(self):
        if self.is_etalon and not len(self.facts):
            return 'no-fact'
        if self.is_etalon:
            matched = [x for x in self.facts if self.name == x.name]
            if not matched:
                return 'bad-age'
        if not self.is_etalon and self.etalon and self.name != self.etalon.name:
            return 'bad-age'
        return ''


class Backup():
    def __init__(self, device, service_name, service_descr, duration, first_day, last_day):
        super().__init__()
        self.device = device
        self.service_name = service_name
        self.duration = duration
        self.first_day = first_day
        self.last_day = last_day
        self.etalon = []
        self.fact = []
        self.work_dir = Path(settings.DJANGO_BACKUP_FOLDER) / device.lower() / service_descr
        self.prefix = device + '-(' + str(duration) + ')-'
        self.fill()

    def get_arh_name_by_day(self, day):
        return self.prefix + day.strftime('%Y.%m.%d') + '.zip'

    def get_arh_age(self, arch, day):
        file_name = arch.replace(self.prefix, '').replace('.zip', '')
        file_date = datetime.strptime(file_name, '%Y.%m.%d').date()
        file_days = (day - file_date).days
        return file_days + 1

    def remove(self, name):
        for x in self.etalon:
            if x.name == name:
                self.etalon.remove(x)
                break

    def get_range(self, pos):
        min_range = int((self.duration+1)**pos)
        max_range = int((self.duration+1)**(pos+1))-1
        return min_range, max_range

    def zip_arh(self, arch_list, pos, day):
        next_pos = pos + 1
        if next_pos >= len(arch_list):
            return
        cur_file_age = self.get_arh_age(arch_list[pos], day)
        cur_min_range, cur_max_range = self.get_range(pos)
        next_file_age = self.get_arh_age(arch_list[next_pos], day)
        next_min_range, next_max_range = self.get_range(next_pos)
        kill = False
        if (cur_file_age < cur_min_range or cur_file_age > cur_max_range) and (next_file_age < next_min_range or next_file_age > next_max_range):
            kill = True # Удалим, если не валиден ни этот ни следующий
        elif (next_file_age >= cur_min_range and next_file_age <= cur_max_range):
            kill = True # Удалим, если следующий соответствует текущему диапазону
        if kill:
            self.remove(arch_list[pos])
            del arch_list[pos]
            self.update_ranges()

    def update_range(self, name, min_range, max_range):
        for x in self.etalon:
            if x.name == name:
                x.min_range = min_range
                x.max_range = max_range
                break

    def update_ranges(self):
        arch_list = [x.name for x in self.etalon]
        npp = 0
        for x in arch_list:
            min_range, max_range = self.get_range(npp)
            self.update_range(x, min_range, max_range)
            npp += 1

    def sizeof_fmt(self, num, suffix='B'):
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(num) < 1024.0:
                return f'{num:3.1f}{unit}{suffix}'
            num /= 1024.0
        return f'{num:.1f}Yi{suffix}'

    def fill(self):
        self.fact.clear()
        for x in self.work_dir.glob('*.zip'):
            size = self.sizeof_fmt(x.stat().st_size)
            arch_age = self.get_arh_age(x.name, self.last_day)
            item = ArchItem(False, x.name, arch_age, size)
            self.fact.append(item)

        self.fact.sort(key=lambda x: x.age)

        arch_list = [x.name for x in self.fact]
        if len(arch_list):
            arch_list.sort(reverse=True)
            first_arch = arch_list[-1]
            file_name = first_arch.replace(self.prefix, '').replace('.zip', '')
            self.first_day = datetime.strptime(file_name, '%Y.%m.%d').date()

        self.etalon.clear()
        cur_day = self.first_day
        _, p0_max_range = self.get_range(0)
        while cur_day <= self.last_day:
            arch_name = self.get_arh_name_by_day(cur_day)
            arch_age = self.get_arh_age(arch_name, self.last_day)
            can_insert = False
            if (not len(self.etalon)):
                can_insert = True
            else:
                x = self.etalon[0]
                if (x.age > p0_max_range) and ((x.age - arch_age) >= self.duration):
                    can_insert = True
            if can_insert:
                item = ArchItem(True, arch_name, arch_age)
                self.etalon.insert(0, item)
                self.update_ranges()
                arch_list = [x.name for x in self.etalon]
                y = 1
                while y < len(arch_list):
                    self.zip_arh(arch_list, y, cur_day)
                    y += 1
            cur_day = cur_day + timedelta(1)
        for e in self.etalon:
            for f in [x for x in self.fact if x.age >= e.min_range and x.age <= e.max_range]:
                e.facts.append(f)
                f.etalon = e

    def valid(self):
        for x in self.etalon:
            if x.ripe() == 0:
                return False
        return True

