import os, zipfile, math, subprocess, time, glob, shutil, smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage

class BackupError(Exception):
    def __init__(self, stage, info):
        self.stage = stage
        self.info = info
    def __str__(self):
        return 'Ошибка на этапе {0}. {1}'.format(self.stage, self.info)

def sizeof_fmt(num, suffix='B'):
    magnitude = int(math.floor(math.log(num, 1024)))
    val = num / math.pow(1024, magnitude)
    if magnitude > 7:
        return '{:.1f}{}{}'.format(val, 'Y', suffix)
    return '{:3.1f}{}{}'.format(val, [' ', ' K', ' M', ' G', ' T', ' P', ' E', ' Z'][magnitude], suffix)

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

class Backup():
    def __init__(self, device, params, first_day, last_day, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params = params
        self.device = device
        self.mode = 'full'
        self.data = []
        self.first_day = first_day
        self.last_day = last_day
        self.content = []
        self.work_dir = params['backup_folder'] + device.lower()

    def count_mode(self, day):
        if not len(self.data):
            self.mode = 'full'
            return
        arh_path_list = list(filter(lambda item: item.mode == 'full', self.data))
        arh_day = datetime.strptime(arh_path_list[0].name, self.device + '-%Y.%m.%d-full.zip').date()
        days = (day - arh_day).days
        if (days == 0) or (days >= (self.params['full_duration_days']-1)):
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
        return file_days + 1

    def remove(self, name):
        for x in self.data:
            if x.name == name:
                self.data.remove(x)
                break

    def get_range(self, mode, pos):
        if mode == 'short':
            min_range = int(2**pos)
            max_range = int(2**(pos+1))-1
        else:
            duration = self.params['full_duration_days']
            min_range = int(duration**pos)
            max_range = int(duration**(pos+1))-1
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
        self.data.clear()
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
            y = 2
            while y < len(mode_list):
                self.zip_arh(mode_list, y, cur_day)
                y += 1
            cur_day = cur_day + timedelta(1)
        self.update_range_by_mode('full')
        self.update_range_by_mode('short')

    def check_name(self, name):
        for x in self.data:
            if x.name == name:
                return True
        return False

    def backup_db(self, zf):
        file = 'mysql_backup.sql'
        command = '"' + self.params['sql_dump'] + '" --user=' + self.params['sql_user'] + ' --password=' + self.params['sql_pass'] + ' --result-file=' + file + ' rusel'
        #self.save_log(False, '[i] command = ', command)
        ret = subprocess.run(command, shell=True)
        if (ret.returncode != 0):
            raise BackupError('backup_db', 'Ошибка создания бэкапа MySQL. Код ошибки: ' + str(ret.returncode))
        sz = os.path.getsize(file)
        self.content.append('   ' + file + '    ' + sizeof_fmt(sz))
        zf.write(file)
        os.remove(file)

    def backup_mail(self, zf):
        ret = subprocess.run('cscript ' + self.params['backup_mail_script_path'] + 'MailBackup.vbs')
        #self.save_log(False, '[i] command = ', command)
        if (ret.returncode != 0):
            raise BackupError('backup_mail', 'Вызов subprocess.run вернул код ошибки ' + str(ret.returncode))
        start_dt = datetime.now()
        total = 0
        fl = glob.glob('HMBackup*.7z')
        qnt = 0
        sz = 0
        sec = int((datetime.now()-start_dt).total_seconds())
        fn = ''
        while (sz == 0) and (sec < self.params['backup_mail_wait']):
            time.sleep(5)
            fl = glob.glob('HMBackup*.7z')
            qnt = len(fl)
            if (qnt > 0):
                fn = fl[0]
                sz = os.path.getsize(fn)
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
            raise BackupError('backup_mail', 'За назначенный таймаут файл архива не был получен.')
        for f in fl:
            total += 1
            sz = os.path.getsize(f)
            self.content.append('   ' + f + '    ' + sizeof_fmt(sz))
            zf.write(f)
            os.remove(f)

    # Архивирование
    def archivate(self):
        if self.mode == 'full':
            dirs = self.params['full_dirs']
        else:
            dirs = self.params['short_dirs']

        if not os.path.exists(self.work_dir):
            os.mkdir(self.work_dir)

        fn = self.device + '-' + datetime.now().strftime('%Y.%m.%d') + '-' + self.mode + '.zip'
        zf = zipfile.ZipFile(self.work_dir + '\\' + fn, 'w')
        for dir in dirs:
            print('Archiving:', dir, '...')
            if (dir == 'mysql'):
                self.backup_db(zf)
            elif (dir == 'email'):
                self.backup_mail(zf)
            else:
                for dirname, subdirs, files in os.walk(dir):
                    zf.write(dirname)
                    for filename in files:
                        zf.write(os.path.join(dirname, filename))
        zf.close()
        sz = os.path.getsize(self.work_dir + '\\' + fn)
        if (sz > 1000):
            self.content.append('   ' + fn + '    ' + sizeof_fmt(sz))
        elif (sz == 0):
            raise BackupError('archivate', 'Не удалось создать архив ' + self.work_dir + '\\' + fn)
        else:
            raise BackupError('archivate', 'Пустой архив ' + self.work_dir + '\\' + fn)

    # Удаление неактуальных архивов
    def zip(self):
        arh_path_list = glob.glob(self.work_dir + '\\*.zip')
        for x in arh_path_list:
            name = x.split('\\')[-1]
            if not self.check_name(name):
                os.remove(x)

    def add_info(self, src, dst):
        if (not self.changed):
            self.changed = True
            self.content.append('  ' + src + ':')
        self.content.append('    ' + dst)
    
    def synch_dir(self, _src, _dst, _folder):
        if (_src == 'nuc'):
            src = self.params['nuc_drive'] + _folder
            dst = self.params['backup_folder'] + _folder
        else:
            src = self.params['backup_folder'] + _folder
            dst = self.params['nuc_drive'] + _folder

        bkp_device = self.device
        self.device = _src.capitalize()
        self.work_dir = self.params['backup_folder'] + _src
        self.fill()
    
        first_time = False
        if not os.path.exists(dst):
            os.mkdir(dst)
            first_time = True
        self.changed = False
        arh_list = glob.glob(src + '\\*.zip')
        for fsrc in arh_list:
            f = fsrc.split('\\')[-1]
            fdst = dst + '\\' + f
            if not self.check_name(f):
                os.remove(fsrc)
                os.remove(fdst)
                continue
            sat = os.path.getatime(fsrc)
            smt = os.path.getmtime(fsrc)
            if first_time or not os.path.exists(fdst):
                print(_dst + '\\' + _folder + '\\' + f, 'copied...')
                shutil.copyfile(fsrc, fdst)
                os.utime(fdst, (sat, smt))
                self.add_info(_src + '\\' + _folder + ' -> ' + _dst + '\\' + _folder, 'Файл скопирован в ' + _dst + '\\' + _folder + '\\' + f)
            else:
                dmt = os.path.getmtime(fdst)
                if (smt != dmt):
                    print(_dst + '\\' + _folder + '\\' + f, 'copied...')
                    shutil.copyfile(src + '\\' + f, fdst)
                    os.utime(fdst, (sat, smt))
                    self.add_info(_src + '\\' + _folder + ' -> ' + _dst + '\\' + _folder, 'Файл обновлен в ' + _dst + '\\' + _folder + '\\' + f)
        self.device = bkp_device
        self.work_dir = self.params['backup_folder'] + self.device.lower()

    # Синхронизация
    def synch(self):
        if (not self.params['syncs'] or (len(self.params['syncs']) == 0)):
            return
        self.content.append('')
        self.content.append('Синхронизация:')
        for s in self.params['syncs']:
            self.synch_dir(s[0], s[1], s[2])

    # Отправка информационного письма
    def send_mail(self, status, info):
        s = smtplib.SMTP(host=self.params['host'], port=25)
        s.starttls()
        s.login(self.params['backup_mail_login'], self.params['backup_mail_pass'])
        msg = EmailMessage()
        msg['From'] = self.params['backup_mail_from']
        msg['To'] = self.params['backup_mail_to']
        msg['Subject']='Архивация на ' + self.device + ' - ' + status
        body = ''
        for str in self.content:
            body = body + str + '\n'
        if (info != ''):
            body = body + '\n' + status + ' ' + info
        msg.set_content(body)
        s.send_message(msg)
        del msg
        s.quit()

    def save_log(self, input_wait, status, info):
        with open(self.params['log_path'] + 'backup.log', 'a') as f:
            f.write(str(datetime.now()) + '   ')
            f.write(status + ' ' + info + '\n')
        for ct in self.content:
            print(ct)
        self.send_mail(status, info)
        if input_wait:
            if info:
                print(info)
            input(status + ' >')

    def run(self, input_wait):
        try:
            self.fill()
            self.content.clear()
            self.count_mode(self.last_day)     # Выбор режима архивирования
            self.archivate()      # Архивирование
            self.zip()            # Удаление неактуальных архивов
            self.synch()          # Синхронизация
            self.save_log(input_wait, 'ok', '')
        except BackupError as be:
            self.save_log(input_wait, '[x]', str(be))
        except Exception as ex:
            self.save_log(input_wait, '[x]', str(ex))
