from datetime import datetime, timedelta


class ArchItem():
    def __init__(self, name, age):
        super().__init__()
        self.name = name
        self.age = age
        self.min_range = None
        self.max_range = None

    def __repr__(self) -> str:
        valid = 1 if self.age >= self.min_range and self.age <= self.max_range else 0
        return f'{valid}: [{self.min_range}-{self.max_range}] - {self.age} - {self.name}'
    
    def ripe(self):
        if self.age >= self.min_range and self.age <= self.max_range:
            return 1
        return 0

class Backup():
    def __init__(self, duration, first_day, last_day):
        super().__init__()
        self.duration = duration
        self.first_day = first_day
        self.last_day = last_day
        self.etalon = []

    def get_arh_name_by_day(self, day):
        return day.strftime('%Y.%m.%d') + '.zip'

    def get_arh_age(self, arch, day):
        file_name = arch.replace('.zip', '')
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

    def fill(self):
        self.etalon.clear()
        cur_day = self.first_day
        p0_min_range, p0_max_range = self.get_range(0)
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
                item = ArchItem(arch_name, arch_age)
                self.etalon.insert(0, item)
                self.update_ranges()
                arch_list = [x.name for x in self.etalon]
                y = 1
                while y < len(arch_list):
                    self.zip_arh(arch_list, y, cur_day)
                    y += 1
            cur_day = cur_day + timedelta(1)

    def valid(self):
        for x in self.etalon:
            if x.ripe() == 0:
                return False
        return True

    def print(self):
        print('--------------------------------------------------')
        print(f'max_date = {self.last_day}')
        for x in self.etalon:
            print(x)

if __name__ == '__main__':
    start = datetime(2022, 12, 1).date()
    stop  = datetime(2022, 12, 2).date()
    test = start
    while test <= stop:
        b = Backup(duration=7, first_day=start, last_day=test)
        b.fill()
        if not b.valid() or (test == stop):
            b.print()
            break
        test = test + timedelta(1)
