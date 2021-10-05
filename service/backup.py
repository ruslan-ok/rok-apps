import os, zipfile, math, shutil, fnmatch, subprocess, smtplib, time
from datetime import datetime
from email.message import EmailMessage
from secret import *

YEAR_DURATION = 365
MONTH_DURATION = 30
WEEK_DURATION = 7

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

    full_mode = False
    content = []
    case = 0

    def read_last(self, name):
        try:
            with open(work_dir + 'last_' + name + '.txt', 'r') as f:
                return f.read()
        except FileNotFoundError:
            return '' # Допустимая ситуация - считаем, что архивирование ещё ни разу не выполнялось
        return ''

    # Выбор режима архивирования
    def count_mode(self):
        self.full_mode = False
        last = self.read_last('full')
        d = 0
        if (last == ''):
            self.full_mode = True
            mode = 'Полный архив (ранее не формировался)'
        else:
            l = datetime.strptime(last, '%Y-%m-%d %H:%M:%S.%f')
            n = datetime.now()
            d = (n - l).days
            self.full_mode = (d >= MONTH_DURATION)
        if self.full_mode:
            mode = 'Полный архив'
        else:
            mode = 'Краткий архив. Дней до полной архивации: ' + str(MONTH_DURATION - d) + '.'
        print(mode)
        self.content.append(mode)
    
    def backup_db(self, zf):
        file = work_dir + 'mysql_backup.sql'
        command = '"' + sql_dump + '" --user=' + sql_user + ' --password=' + sql_pass + ' --result-file=' + file + ' rusel'
        return_code = subprocess.call(command, shell = True)
        if (return_code != 0):
            raise BackupError('backup_db', 'Ошибка создания бэкапа MySQL. Код ошибки: ' + return_code.__str__())
        sz = os.path.getsize(file)
        self.content.append('   ' + file + '    ' + sizeof_fmt(sz))
        zf.write(file)
        os.remove(file)

    def backup_mail(self, zf):
        return_code = subprocess.call(work_dir + 'MailBackup.vbs', shell = True)
        if (return_code != 0):
            raise BackupError('backup_mail', 'Вызов subprocess.call вернул код ошибки ' + return_code.__str__())
        time.sleep(mail_wait)
        total = 0
        for file in fnmatch.filter(os.listdir('.'), work_dir + 'HMBackup*.7z'):
            total += 1
            sz = os.path.getsize(file)
            self.content.append('   ' + file + '    ' + sizeof_fmt(sz))
            zf.write(file)
            os.remove(file)
        if (total == 0):
            raise BackupError('backup_mail', 'За назначенный таймаут файл архива не был получен.')

    # Архивирование
    def archivate(self):
        if self.full_mode:
            dirs = full_dirs
        else:
            dirs = short_dirs

        try:
            os.mkdir(work_dir + 'temp')
        except FileExistsError:
            pass

        fn = device + '-' + datetime.now().strftime('%Y.%m.%d-%H.%M.%S')
        zf = zipfile.ZipFile(work_dir + 'temp/' + fn + '.zip', 'w')
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
        sz = os.path.getsize(work_dir + 'temp/' + fn + '.zip')
        if (sz > 1000):
            self.content.append('   ' + fn + '.zip    ' + sizeof_fmt(sz))
        elif (sz == 0):
            raise BackupError('archivate', 'Не удалось создать архив ' + work_dir + 'temp/' + fn + '.zip')
        else:
            raise BackupError('archivate', 'Пустой архив ' + work_dir + 'temp/' + fn + '.zip')

    # Если содержимое какого-то каталога удалялось, то его можно пометить и очистить его заркало в процессе синхронизации
    def mark_for_clear(self, dir):
        with open(dir + '/__clear__.txt', 'a') as f:
            f.write('clear me')

    # Определение возраста архива в указанной папке
    def arch_age(self, dir, max_duration):
        n = datetime.now()
        for file in fnmatch.filter(os.listdir(dir), device + '-????.??.??-??.??.??.zip'): # в указанной папке ищем любой подходящий под наш шаблон архив
            ss = file[len(device)+1:-4]
            mt = datetime.strptime(ss, '%Y.%m.%d-%H.%M.%S')
            return (n - mt).days # вернем количество дней от даты его модификации
        return max_duration
    
    # Ротация
    def rotate(self):
        if self.full_mode:
            max_duration = YEAR_DURATION
            max_dir = work_dir + 'year2'
            med_dir = work_dir + 'year1'
            min_dir = work_dir + 'month'
        else:
            max_duration = WEEK_DURATION
            max_dir = work_dir + 'week2'
            med_dir = work_dir + 'week1'
            min_dir = work_dir + 'day'
        tmp_dir = work_dir + 'temp'

        if not os.path.exists(max_dir):
            shutil.copytree(tmp_dir, max_dir, dirs_exist_ok=True)
            self.mark_for_clear(max_dir)
            self.content.append('   Копия сохранена в ' + max_dir)

        if not os.path.exists(med_dir):
            shutil.copytree(tmp_dir, med_dir, dirs_exist_ok=True)
            self.mark_for_clear(med_dir)
            self.content.append('   Архив сохранен в ' + med_dir)
        else:
            age = self.arch_age(med_dir, max_duration)
            if (age >= max_duration):
                print('Выполняется ротация')
                shutil.rmtree(max_dir, ignore_errors = True)
                os.rename(med_dir, max_dir)
                os.rename(min_dir, med_dir)
                self.mark_for_clear(max_dir)
                self.mark_for_clear(med_dir)
                self.content.append('   Ротация: ' + tmp_dir + ' -> ' + min_dir + ' -> ' + med_dir + ' -> ' + max_dir)
            else:
                self.content.append('   Архив сохранен в ' + min_dir + '. Дней до ротации: ' + str(max_duration - age))

        shutil.rmtree(min_dir, ignore_errors = True)
        os.rename(tmp_dir, min_dir)
        self.mark_for_clear(min_dir)

    def add_info(self, src, dst):
        if (self.case == 0):
            self.case = 1
            self.content.append('  ' + src + ':')
        self.content.append('    ' + dst)
    
    def clear_dir(self, dir):
        for filename in os.listdir(dir):
            file_path = os.path.join(dir, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        
    def synch_dir(self, _src, _dst, _folder):
        if (_src == 'nuc'):
            src = nuc_drive + _folder
            dst = backup_folder + _folder
        else:
            src = backup_folder + _folder
            dst = nuc_drive + _folder
    
        self.case = 0
        for dirname, subdirs, files in os.walk(src):
            part = dirname[len(src)+1:]
            if (part != ''):
                part = '\\' + part

            test = dst + part
    
            zzz = False
            if not os.path.exists(test):
                os.mkdir(test)
                zzz = True
            else:
                if os.path.isfile(src + part + '/__clear__.txt'):
                    self.clear_dir(test)
                    zzz = True
    
            for f in files:
                if (f == '__clear__.txt'):
                    os.remove(src + part + '\\' + f)
                    continue
                fsrc = src + part + '\\' + f
                fdst = test + '\\' + f
                sat = os.path.getatime(fsrc)
                smt = os.path.getmtime(fsrc)
                if zzz or not os.path.exists(fdst):
                    print(_dst + '\\' + _folder + part + '\\' + f, 'copied...')
                    shutil.copyfile(fsrc, fdst)
                    os.utime(fdst, (sat, smt))
                    self.add_info(_src + '\\' + _folder + ' -> ' + _dst + '\\' + _folder, 'Файл скопирован в ' + _dst + '\\' + _folder + part + '\\' + f)
                else:
                    dmt = os.path.getmtime(fdst)
                    if (smt != dmt):
                        print(_dst + '\\' + _folder + part + '\\' + f, 'copied...')
                        shutil.copyfile(fsrc, fdst)
                        os.utime(fdst, (sat, smt))
                        self.add_info(_src + '\\' + _folder + ' -> ' + _dst + '\\' + _folder, 'Файл обновлен в ' + _dst + '\\' + _folder + part + '\\' + f)
    
        if (self.case == 0):
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
        s = smtplib.SMTP(host='rusel.by', port=25)
        s.starttls()
        s.login(mail_login, mail_pass)
        msg = EmailMessage()
        msg['From'] = mail_from
        msg['To'] = mail_to
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

    # Фиксация времени архивирования
    def fix_time(self):
        if self.full_mode:
            tail = 'full'
        else:
            tail = 'short'
        with open(work_dir + 'last_' + tail + '.txt', 'w') as f:
            f.write(datetime.now().__str__())

    def save_log(self, input_wait, status, info):
        with open(work_dir + 'backup.log', 'a') as f:
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
            self.rotate()         # Ротация
            self.synch()          # Синхронизация
            self.fix_time()       # Фиксация времени архивирования
            self.save_log(input_wait, 'ok', '')
        except BackupError as be:
            self.save_log(input_wait, '[x]', str(be))
        except Exception as ex:
            self.save_log(input_wait, '[x]', str(ex))
            

if __name__ == '__main__':
    x = Backup()
    x.run(False)
