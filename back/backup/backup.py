import os, glob, pyzipper, subprocess, time
from datetime import datetime, timedelta
from backup.sync import Sync
from logs.logger import get_logger, set_service
from task.const import ROLE_BACKUP_SHORT, ROLE_BACKUP_FULL

except_dirs = [
    'apps\\rusel\\.git',
    'apps\\rusel\\front\\dist',
    'apps\\rusel\\front\\media',
    'apps\\rusel\\front\\node_modules',
]

logger = get_logger(__name__)

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
    def __init__(self, device, service_name, service_descr, duration, folders, first_day, last_day):
        super().__init__()
        self.device = device
        self.service_name = service_name
        self.duration = duration
        self.folders = [x.replace('\\\\', '\\') for x in folders]
        self.first_day = first_day
        self.last_day = last_day
        self.etalon = []
        self.fact = []
        self.content = []
        self.backup_folder = os.environ.get('DJANGO_BACKUP_FOLDER')
        self.service_descr = service_descr
        self.work_dir = self.backup_folder + device.lower() + '\\' + service_descr
        self.prefix = device + '-(' + str(duration) + ')-'
        self.fill()
        self.arch_pwrd = os.environ.get('DJANGO_BACKUP_PWRD')
        set_service(logger, service_name)

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
        logger.info('+backup_db() started')
        file = 'mysql_backup.sql'
        sql_util = '"' + os.environ.get('DJANGO_BACKUP_SQL_UTIL', '') + '"'
        logger.debug(f'sql_util = {sql_util}')
        sql_user = os.environ.get('DJANGO_BACKUP_SQL_USER', '')
        logger.debug(f'sql_user = {sql_user}')
        sql_pass = os.environ.get('DJANGO_BACKUP_SQL_PWRD', '')
        logger.debug(f'sql_pass = {sql_pass}')
        sql_schema = os.environ.get('DJANGO_BACKUP_SQL_SCHEMA', '')
        logger.debug(f'sql_schema = {sql_schema}')
        command = sql_util + ' --user=' + sql_user + ' --password=' + sql_pass + ' --result-file=' + file + ' ' + sql_schema
        logger.debug(f'command = {command}')
        ret = subprocess.run(command, shell=True)
        logger.debug(f'ret.returncode = {ret.returncode}')
        if (ret.returncode != 0):
            logger.error('Ошибка создания бэкапа MySQL. Код ошибки: ' + str(ret.returncode))
            return
        sz = os.path.getsize(file)
        self.content.append('   ' + file + '    ' + self.sizeof_fmt(sz))
        zf.write(file)
        logger.info('remove ' + file)
        os.remove(file)
        logger.info('-backup_db() finished')

    def backup_mail(self, zf):
        logger.info('+backup_mail() started')
        script = os.environ.get('DJANGO_BACKUP_MAIL_UTIL', '')
        wait_time = int(os.environ.get('DJANGO_BACKUP_MAIL_WAIT', '600'))
        ret = subprocess.run('cscript ' + script)
        if (ret.returncode != 0):
            logger.error('backup_mail: Вызов subprocess.run вернул код ошибки ' + str(ret.returncode))
            return
        start_dt = datetime.now()
        total = 0
        sz = 0
        sec = int((datetime.now()-start_dt).total_seconds())
        while (sz == 0) and (sec < wait_time):
            time.sleep(5)
            fl = glob.glob(self.work_dir + '\\..\\HMBackup*.7z')
            logger.debug('backup_mail: Количество найденных архивов ' + str(len(fl)))
            if (len(fl) > 0):
                fn = fl[0]
                sz = os.path.getsize(fn)
                logger.info('backup_mail: Размер архива ' + str(sz))
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
            logger.debug(f'{sec=}, {sz=}, {status=}, {fn=}')
            if (status != 'ok'):
                sz = 0
        if (sz == 0):
            logger.error('backup_mail: За назначенный таймаут файл архива не был получен.')
            return
        for f in fl:
            total += 1
            sz = os.path.getsize(f)
            self.content.append('   ' + f + '    ' + self.sizeof_fmt(sz))
            zf.write(f, arcname=f.split(self.work_dir + '\\..\\')[1])
            logger.info('remove ' + f)
            os.remove(f)
        logger.info('-backup_mail() finished')

    def backup_env(self, zf):
        logger.info('+backup_env() started')
        file = 'env.csv'
        with open(file, 'w', encoding='utf-8') as f:
            f.write('name, value\n')
            for name, value in os.environ.items():
                f.write(f'{name}, {value}\n')
        zf.write(file)
        os.remove(file)
        logger.info('-backup_env() finished')

    def backup_reqs(self, zf):
        logger.info('+backup_reqs() started')
        python_exe = os.environ.get('DJANGO_PYTHON', 'python.exe')
        reqs = subprocess.check_output([python_exe, '-Xfrozen_modules=off', '-m', 'pip', 'freeze'], universal_newlines=True)
        file = 'reqs.txt'
        with open(file, 'w', encoding='utf-8') as f:
            f.write(reqs)
        zf.write(file)
        os.remove(file)
        logger.info('-backup_reqs() finished')


    # Архивирование
    def archivate(self):
        logger.info('+archivate() started')

        dir_name = self.work_dir

        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

        fn = self.prefix + datetime.now().strftime('%Y.%m.%d') + '.zip'
        dir_file = self.work_dir + '\\' + fn

        zf = pyzipper.AESZipFile(dir_file, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES)
        zf.setpassword(str.encode(self.arch_pwrd))
        for dir in self.folders:
            logger.info(f'Archiving: {dir}...')
            if (dir == 'mysql'):
                self.backup_db(zf)
            elif (dir == 'email'):
                self.backup_mail(zf)
            else:
                if not os.path.exists(dir):
                    logger.warning('archiving: Folder does not exist: ' + dir)
                    continue
                logger.info('archiving: ' + dir)
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
            logger.error('archivate: Не удалось создать архив ' + dir_file)
        else:
            logger.error('archivate: Пустой архив ' + dir_file)
        logger.info('-archivate() finished')

    def check_name(self, name):
        for x in self.etalon:
            if x.name == name:
                return True
        return False

    # Удаление неактуальных архивов
    def zipping(self):
        logger.info('+zipping() started')
        arh_path_list = glob.glob(self.work_dir + '\\*.zip')
        for x in arh_path_list:
            name = x.split('\\')[-1]
            if not self.check_name(name):
                logger.info('remove: ' + x)
                os.remove(x)
        logger.info('-zipping() finished')

    # Синхронизация
    def synch(self):
        so = Sync(self.service_name)
        so.run()

    def run(self):
        logger.info('start: ' + self.device)
        try:
            self.content.clear()
            self.archivate() # Архивирование
            self.zipping()   # Удаление неактуальных архивов
            self.synch()     # Синхронизация
        except Exception as ex:
            logger.exception(ex)
        logger.info('finish: ' + self.device)

def test_backup_zipping():
    start = datetime(2022, 10, 15).date()
    stop  = datetime.today().date()
    backup = Backup('Vivo', service_name=ROLE_BACKUP_SHORT, service_descr='Ежедневный бэкап', duration=1, folders='', first_day=start, last_day=stop)
    backup.run()
    #backup = Backup('Vivo', service_name=ROLE_BACKUP_FULL, service_descr='Еженедельный бэкап', duration=7, folders='', first_day=start, last_day=stop)
    #backup.zipping()

if __name__ == '__main__':
    test_backup_zipping()