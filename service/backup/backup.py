import os, zipfile, math, shutil, subprocess, smtplib, time, glob, fnmatch
from datetime import date, datetime
from email.message import EmailMessage
from secret import *

class BackupError(Exception):
    def __init__(self, stage, info):
        self.stage = stage
        self.info = info
    def __str__(self):
        return 'Ошибка на этапе {0}. {1}'.format(self.stage, self.info)

def sizeof_fmt(num, suffix = 'B'):
    magnitude = int(math.floor(math.log(num, 1024)))
    val = num / math.pow(1024, magnitude)
    if magnitude > 7:
        return '{:.1f}{}{}'.format(val, 'Y', suffix)
    return '{:3.1f}{}{}'.format(val, [' ', ' K', ' M', ' G', ' T', ' P', ' E', ' Z'][magnitude], suffix)
    

class Backup:

    mode = 'full'
    content = []
    changed = False
    arh_list = []

    # Выбор режима архивирования
    def count_mode(self):
        arh_path_list = glob.glob(work_dir + '\\' + device + '-*-full.zip')
        if not len(arh_path_list):
            self.mode = 'full'
            return
        arh_list_tmp = [x.split('\\')[-1] for x in arh_path_list]
        arh_list_tmp.sort(reverse=True)
        self.arh_list = arh_list_tmp
        arh_day = datetime.strptime(self.arh_list[-1], device + '-%Y.%m.%d-full.zip').date()
        days = (date.today() - arh_day).days
        if (days == 0) or (days >= full_duration_days):
            self.mode = 'full'
            return
        self.mode = 'short'
        return

    def backup_db(self, zf):
        file = 'mysql_backup.sql'
        command = '"' + sql_dump + '" --user=' + sql_user + ' --password=' + sql_pass + ' --result-file=' + file + ' rusel'
        return_code = subprocess.call(command, shell = True)
        if (return_code != 0):
            raise BackupError('backup_db', 'Ошибка создания бэкапа MySQL. Код ошибки: ' + return_code.__str__())
        sz = os.path.getsize(file)
        self.content.append('   ' + file + '    ' + sizeof_fmt(sz))
        zf.write(file)
        os.remove(file)

    def backup_mail(self, zf):
        return_code = subprocess.call('MailBackup.vbs', shell = True)
        if (return_code != 0):
            raise BackupError('backup_mail', 'Вызов subprocess.call вернул код ошибки ' + return_code.__str__())
        start_dt = datetime.now()
        total = 0
        fl = glob.glob('HMBackup*.7z')
        qnt = 0
        sz = 0
        sec = int((datetime.now()-start_dt).total_seconds())
        fn = ''
        while (sz == 0) and (sec < backup_mail_wait):
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
            dirs = full_dirs
        else:
            dirs = short_dirs

        if not os.path.exists(work_dir):
            os.mkdir(work_dir)

        fn = device + '-' + datetime.now().strftime('%Y.%m.%d') + '-' + self.mode + '.zip'
        zf = zipfile.ZipFile(work_dir + '\\' + fn, 'w')
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
        sz = os.path.getsize(work_dir + '\\' + fn)
        if (sz > 1000):
            self.content.append('   ' + fn + '    ' + sizeof_fmt(sz))
        elif (sz == 0):
            raise BackupError('archivate', 'Не удалось создать архив ' + work_dir + '\\' + fn)
        else:
            raise BackupError('archivate', 'Пустой архив ' + work_dir + '\\' + fn)

    # Определение возраста архива
    def get_arch_age(self, arh, day):
        file_date = datetime.strptime(arh.split('.')[0], device + '-%Y.%m.%d-' + self.mode).date()
        file_days = (day - file_date).days
        return file_days

    # Проверка и при необходимости удаление архива в указанной позиции  из списка имеющихся
    def zip_arh(self, pos, day):
        file_age = self.get_arh_age(self.arh_list[pos], day)
        min_range = 2**(pos-1)+1
        max_range = 2**pos
        if file_age < min_range or file_age > max_range:
            if pos < len(self.arh_list)-1:
                next_file_age = self.get_arh_age(self.arh_list[pos+1], day)
                if next_file_age >= min_range and next_file_age <= max_range:
                    self.content.append('   Удален архив ' + self.arh_list[pos])
                    del self.arh_list[pos]

    # Удаление неактуальных архивов
    def zip(self):
        arh_path_list = glob.glob(work_dir + '\\' + device + '-*-' + self.mode + '.zip')
        arh_list_tmp = [x.split('\\')[-1] for x in arh_path_list]
        arh_list_tmp.sort(reverse=True)
        self.arh_list = arh_list_tmp
        for y in range(2, len(self.arh_list)-1):
            self.zip_arh(y, date.today())

    def add_info(self, src, dst):
        if (not self.changed):
            self.changed = True
            self.content.append('  ' + src + ':')
        self.content.append('    ' + dst)
    
    def synch_dir(self, _src, _dst, _folder):
        if (_src == 'nuc'):
            src = nuc_drive + _folder
            dst = backup_folder + _folder
        else:
            src = backup_folder + _folder
            dst = nuc_drive + _folder
    
        first_time = False
        if not os.path.exists(dst):
            os.mkdir(dst)
            first_time = True
        self.changed = False
        arh_list = glob.glob(src + '\\*.zip')
        for fsrc in arh_list:
            f = fsrc.split('\\')[-1]
            fdst = dst + '\\' + f
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
    
        if (not self.changed):
            self.content.append('   ' + _src + '\\' + _folder + ' -> ' + _dst + '\\' + _folder + ' - без изменений.')

    # Синхронизация
    def synch(self):
        if (not syncs or (len(syncs) == 0)):
            return
        self.content.append('')
        self.content.append('Синхронизация:')
        for s in syncs:
            self.synch_dir(s[0], s[1], s[2])

    # Отправка информационного письма
    def send_mail(self, status, info):
        s = smtplib.SMTP(host=host, port=25)
        s.starttls()
        s.login(backup_mail_login, backup_mail_pass)
        msg = EmailMessage()
        msg['From'] = backup_mail_from
        msg['To'] = backup_mail_to
        msg['Subject']='Архивация на ' + device + ' - ' + status
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
        with open(log_path + 'backup.log', 'a') as f:
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
            self.content.clear()
            self.count_mode()     # Выбор режима архивирования
            self.archivate()      # Архивирование
            self.zip()            # Удаление неактуальных архивов
            self.synch()          # Синхронизация
            self.save_log(input_wait, 'ok', '')
        except BackupError as be:
            self.save_log(input_wait, '[x]', str(be))
        except Exception as ex:
            self.save_log(input_wait, '[x]', str(ex))
            

if __name__ == '__main__':
    x = Backup()
    x.run(False)
