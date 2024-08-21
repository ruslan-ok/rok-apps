import os, pyzipper
from pathlib import Path
from prefect import flow, task
from pydantic import BaseModel
from datetime import datetime, timedelta
from backup_params import (
    DEVICE,
    BACKUP_FOLDER,
    BACKUP_PWRD,
    PERIODICITY,
    EXCEPT_DIRS,
)

class BackupParams(BaseModel):
    name: str
    duration: int
    folders: list[str]

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

    def __init__(self, params: BackupParams):
        super().__init__()
        self.name = params.name
        self.duration = params.duration
        self.folders = params.folders
        self.work_dir = Path(BACKUP_FOLDER) / DEVICE.lower() / params.name
        self.prefix = DEVICE.split('-')[0] + '-(' + str(params.duration) + ')-'
        self.first_day = datetime(2022, 10, 15).date()
        self.last_day = datetime.today().date()
        self.etalon = []
        self.fact = []
        self.fill()

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

    def sizeof_fmt(self, num, suffix='B'):
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(num) < 1024.0:
                return f'{num:3.1f}{unit}{suffix}'
            num /= 1024.0
        return f'{num:.1f}Yi{suffix}'

    def get_arh_age(self, arch, day):
        file_name = arch.replace(self.prefix, '').replace('.zip', '')
        file_date = datetime.strptime(file_name, '%Y.%m.%d').date()
        file_days = (day - file_date).days
        return file_days + 1

    def get_range(self, pos):
        min_range = int((self.duration+1)**pos)
        max_range = int((self.duration+1)**(pos+1))-1
        return min_range, max_range

    def get_arh_name_by_day(self, day):
        return self.prefix + day.strftime('%Y.%m.%d') + '.zip'

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

    def remove(self, name):
        for x in self.etalon:
            if x.name == name:
                self.etalon.remove(x)
                break

    def backup(self):
        if self.ripe():
            self.archivate() # Архивирование
            self.zipping()   # Удаление неактуальных архивов

    @task(tags=['backup', 'ripe'])
    def ripe(self):
        if not len(self.etalon):
            return False
        actual_etalon = self.etalon[0]
        if self.fact:
            last_fact = self.fact[0]
            if last_fact.age >= actual_etalon.min_range and last_fact.age <= actual_etalon.max_range:
                return False
        return True

    # Архивирование
    def archivate(self):
        if not self.work_dir.exists():
            os.makedirs(str(self.work_dir))

        fn = self.prefix + datetime.now().strftime('%Y.%m.%d') + '.zip'
        dir_file = str(self.work_dir / fn)

        zf = pyzipper.AESZipFile(dir_file, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES)
        zf.setpassword(str.encode(BACKUP_PWRD))
        for folder in self.folders:
            dir = Path(folder)
            if not dir.exists():
                print('Archiving: Folder does not exist: ' + str(dir))
                continue
            name = 'Backup: ' + str(dir)
            self.backup_dir(zf, dir, name)
        zf.close()

    @task(task_run_name='{name}', tags=['backup', 'dir'])
    def backup_dir(self, zf, dir, name):
        for dirname, _, files in dir.walk():
            skip = False
            for x in EXCEPT_DIRS:
                if x in dirname.as_posix():
                    skip = True
                    break
            if skip:
                continue
            zf.write(str(dirname))
            for filename in files:
                zf.write(str(dirname / filename))

    # Удаление неактуальных архивов
    @task(tags=['backup', 'zipping'])
    def zipping(self):
        arh_path_list = self.work_dir.glob('*.zip')

        # Предварительный анализ файлов архивов
        arhs = []
        for x in arh_path_list:
            arh_name = x.name
            arh_age = self.get_arh_age(arh_name, datetime.today().date())
            etalon = None
            matched = False
            for et in self.etalon:
                if arh_age >= et.min_range and arh_age <= et.max_range:
                    etalon = et
                    matched = (arh_name == et.name)
                    break
            if etalon:
                arhs.append({
                    "etalon_age": etalon.age,
                    "matched": matched,
                    "full_name": x,
                    "arh_name": arh_name,
                    "arh_age": arh_age,
                })

        # Группировка файлов архивов по диапазонам эталона
        ages = {}
        for x in arhs:
            et_age = x["etalon_age"]
            if et_age not in ages.keys():
                ages[et_age] = {
                    "matched": [],
                    "unmatched": [],
                }
            if x["matched"]:
                ages[et_age]["matched"].append(x["arh_name"])
            else:
                ages[et_age]["unmatched"].append({
                    "full_name": x["full_name"],
                    "arh_age": x["arh_age"],
                })

        # Удаление лишних
        for rng in ages.values():
            if (len(rng["matched"]) + len(rng["unmatched"])) > 1:
                if len(rng["matched"]):
                    for x in rng["unmatched"]:
                        x["full_name"].unlink()
                else:
                    max_age = 0
                    the_best = None
                    for x in rng["unmatched"]:
                        if x["arh_age"] > max_age:
                            max_age = x["arh_age"]
                            the_best = x["full_name"]
                            break
                    if the_best:
                        the_best.unlink()


@flow(flow_run_name='Check backup {params.name}', log_prints=True)
def backup_periodically(params: BackupParams):
    z = Backup(params)
    z.backup()

if __name__ == '__main__':
    for period in PERIODICITY:
        params = BackupParams(name=period['name'], duration=period['duration'], folders=period['folders'])
        backup_periodically(params)
