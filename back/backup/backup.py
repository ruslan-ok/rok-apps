import os, glob, pyzipper, subprocess, time, sys
from datetime import datetime, timedelta
from backup.sync import Sync
from logs.models import EventType
# from enum import Enum

# class EventType(Enum):
#         ERROR = 'error'
#         WARNING = 'warning'
#         INFO = 'info'
#         DEBUG = 'debug'

except_dirs = [
    'apps\\rusel\\.git',
    'apps\\rusel\\front\\dist',
    'apps\\rusel\\front\\media',
    'apps\\rusel\\front\\node_modules',
]

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
    def __init__(self, device, service_name, duration, folders, first_day, last_day, log_event=None):
        super().__init__()
        self.device = device
        self.duration = duration
        self.folders = [x.replace('\\\\', '\\') for x in folders]
        self.first_day = first_day
        self.last_day = last_day
        self.etalon = []
        self.fact = []
        self.content = []
        self.log_event = log_event
        self.backup_folder = os.environ.get('DJANGO_BACKUP_FOLDER')
        self.service_name = service_name
        self.work_dir = self.backup_folder + device.lower() + '\\' + service_name
        self.prefix = device + '-(' + str(duration) + ')-'
        self.fill()
        self.arch_pwrd = os.environ.get('DJANGO_BACKUP_PWRD')

    def log(self, type, name, info, send_mail=False, one_per_day=False):
        if self.log_event:
            self.log_event(type, name, info, send_mail=send_mail, one_per_day=one_per_day)

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
        for x in glob.glob(self.work_dir + '\\*.zip'):
            size = self.sizeof_fmt(os.path.getsize(x))
            arch_name = x.replace(self.work_dir + '\\', '')
            arch_age = self.get_arh_age(arch_name, self.last_day)
            item = ArchItem(arch_name, arch_age)
            item.size = size
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
        for e in self.etalon:
            e.has_fact = False
            for f in self.fact:
                if e.name == f.name:
                    e.has_fact = True
                    break
        for f in self.fact:
            f.valid=(1 if self.check_name(f.name) else 0)

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

    def ripe(self):
        if not len(self.etalon):
            return False
        actual = self.etalon[0]
        ret = True
        for x in self.fact:
            age = self.get_arh_age(x.name, datetime.today().date())
            if age >= actual.min_range and age <= actual.max_range:
                ret = False
                break;
        return ret

    def backup_db(self, zf):
        self.log(EventType.INFO, 'method', '+backup_db() started')
        file = 'mysql_backup.sql'
        sql_util = '"' + os.environ.get('DJANGO_BACKUP_SQL_UTIL', '') + '"'
        # self.log(EventType.INFO, 'variable', f'sql_util = {sql_util}')
        sql_user = os.environ.get('DJANGO_BACKUP_SQL_USER', '')
        # self.log(EventType.INFO, 'variable', f'sql_user = {sql_user}')
        sql_pass = os.environ.get('DJANGO_BACKUP_SQL_PWRD', '')
        # self.log(EventType.INFO, 'variable', f'sql_pass = {sql_pass}')
        sql_schema = os.environ.get('DJANGO_BACKUP_SQL_SCHEMA', '')
        # self.log(EventType.INFO, 'variable', f'sql_schema = {sql_schema}')
        command = sql_util + ' --user=' + sql_user + ' --password=' + sql_pass + ' --result-file=' + file + ' ' + sql_schema
        # self.log(EventType.INFO, 'variable', f'command = {command}')
        ret = subprocess.run(command, shell=True)
        # self.log(EventType.INFO, 'variable', f'ret.returncode = {ret.returncode}')
        if (ret.returncode != 0):
            self.log(EventType.ERROR, 'backup_db', 'Ошибка создания бэкапа MySQL. Код ошибки: ' + str(ret.returncode), send_mail=True)
            return
        sz = os.path.getsize(file)
        self.content.append('   ' + file + '    ' + self.sizeof_fmt(sz))
        zf.write(file)
        self.log(EventType.INFO, 'remove', file)
        os.remove(file)
        self.log(EventType.INFO, 'method', '-backup_db() finished')

    def backup_mail(self, zf):
        self.log(EventType.INFO, 'method', '+backup_mail() started')
        script = os.environ.get('DJANGO_BACKUP_MAIL_UTIL', '')
        wait_time = int(os.environ.get('DJANGO_BACKUP_MAIL_WAIT', '600'))
        ret = subprocess.run('cscript ' + script)
        #self.save_log(False, '[i] command = ', command)
        if (ret.returncode != 0):
            self.log(EventType.ERROR, 'backup_mail', 'Вызов subprocess.run вернул код ошибки ' + str(ret.returncode), send_mail=True)
            return
        start_dt = datetime.now()
        total = 0
        sz = 0
        sec = int((datetime.now()-start_dt).total_seconds())
        while (sz == 0) and (sec < wait_time):
            time.sleep(5)
            fl = glob.glob(self.work_dir + '\\..\\HMBackup*.7z')
            # self.log(EventType.INFO, 'backup_mail', 'Количество найденных архивов ' + str(len(fl)))
            if (len(fl) > 0):
                fn = fl[0]
                sz = os.path.getsize(fn)
                # self.log(EventType.INFO, 'backup_mail', 'Размер архива ' + str(sz))
            sec = int((datetime.now()-start_dt).total_seconds())
            status = 'ok'
            if (sz < 200000000):
                sz = 0
            else:
                try:
                    with open(fn, 'rb') as f:
                        f.read()
                        status = 'ok'
                except Exception as ex:
                    status = '[x] ' + str(ex)
            #print('sec = {}, qnt = {}, sz = {}, status = {}, fn = {}'.format(sec, qnt, sz, status, fn))
            if (status != 'ok'):
                sz = 0
        if (sz == 0):
            self.log(EventType.ERROR, 'backup_mail', 'За назначенный таймаут файл архива не был получен.', send_mail=True)
            return
        for f in fl:
            total += 1
            sz = os.path.getsize(f)
            self.content.append('   ' + f + '    ' + self.sizeof_fmt(sz))
            zf.write(f, arcname=f.split(self.work_dir + '\\..\\')[1])
            self.log(EventType.INFO, 'remove', f)
            os.remove(f)
        self.log(EventType.INFO, 'method', '-backup_mail() finished')

    def backup_env(self, zf):
        self.log(EventType.INFO, 'method', '+backup_env() started')
        file = 'env.csv'
        with open(file, 'w', encoding='utf-8') as f:
            f.write('name, value\n')
            for name, value in os.environ.items():
                f.write(f'{name}, {value}\n')
        zf.write(file)
        os.remove(file)
        self.log(EventType.INFO, 'method', '-backup_env() finished')

    def backup_reqs(self, zf):
        self.log(EventType.INFO, 'method', '+backup_reqs() started')
        python_exe = os.environ.get('DJANGO_PYTHON', 'python.exe')
        reqs = subprocess.check_output([python_exe, '-Xfrozen_modules=off', '-m', 'pip', 'freeze'], universal_newlines=True)
        file = 'reqs.txt'
        with open(file, 'w', encoding='utf-8') as f:
            f.write(reqs)
        zf.write(file)
        os.remove(file)
        self.log(EventType.INFO, 'method', '-backup_reqs() finished')


    # Архивирование
    def archivate(self):
        self.log(EventType.INFO, 'method', '+archivate() started')

        dir_name = self.work_dir

        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

        fn = self.prefix + datetime.now().strftime('%Y.%m.%d') + '.zip'
        dir_file = self.work_dir + '\\' + fn

        zf = pyzipper.AESZipFile(dir_file, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES)
        zf.setpassword(str.encode(self.arch_pwrd))
        for dir in self.folders:
            tm = datetime.now().strftime('%H:%M:%S')
            print(f'{tm} Archiving: {dir}...')
            if (dir == 'mysql'):
                self.backup_db(zf)
            elif (dir == 'email'):
                self.backup_mail(zf)
            else:
                if not os.path.exists(dir):
                    self.log(EventType.WARNING, 'archiving', 'Folder does not exist: ' + dir)
                    continue
                self.log(EventType.INFO, 'archiving', dir)
                for dirname, subdirs, files in os.walk(dir):
                    skip = False
                    for x in except_dirs:
                        if x in dirname:
                            skip = True
                            break
                    if skip:
                        continue
                    zf.write(dirname)
                    for filename in files:
                        zf.write(os.path.join(dirname, filename))
        self.backup_env(zf)
        self.backup_reqs(zf)
        zf.close()
        sz = os.path.getsize(dir_file)
        if (sz > 1000):
            self.content.append('   ' + fn + '    ' + self.sizeof_fmt(sz))
        elif (sz == 0):
            self.log(EventType.ERROR, 'archivate', 'Не удалось создать архив ' + dir_file, send_mail=True)
        else:
            self.log(EventType.ERROR, 'archivate', 'Пустой архив ' + dir_file, send_mail=True)
        self.log(EventType.INFO, 'method', '-archivate() finished')

    def check_name(self, name):
        for x in self.etalon:
            if x.name == name:
                return True
        return False

    # Удаление неактуальных архивов
    def zipping(self):
        self.log(EventType.INFO, 'method', '+zipping() started')
        arh_path_list = glob.glob(self.work_dir + '\\*.zip')
        for x in arh_path_list:
            name = x.split('\\')[-1]
            if not self.check_name(name):
                self.log(EventType.INFO, 'remove', x)
                os.remove(x)
        self.log(EventType.INFO, 'method', '-zipping() finished')

    # Синхронизация
    def synch(self):
        so = Sync(self.log)
        so.run()

    def run(self):
        self.log(EventType.INFO, 'method', f'+run({self.device}, {self.duration}) started')
        try:
            self.content.clear()
            self.archivate() # Архивирование
            self.zipping()   # Удаление неактуальных архивов
            self.synch()     # Синхронизация
        except Exception as ex:
            self.log(EventType.ERROR, 'exception', str(ex), send_mail=True)
        self.log(EventType.INFO, 'method', '-run() finished')

def test_backup_zipping():
    start = datetime(2022, 10, 15).date()
    stop  = datetime.today().date()
    backup = Backup('Vivo', service_name='Еженедельный бэкап', duration=7, folders='', first_day=start, last_day=stop)
    backup.zipping()

if __name__ == '__main__':
    test_backup_zipping()