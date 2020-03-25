import os, zipfile, math, shutil, fnmatch, subprocess, smtplib, time
from enum import Enum
from datetime import datetime
from email.message import EmailMessage
from secret import device, mail_login, mail_pass, mail_from, mail_to, mail_wait, short_dirs, full_dirs, sql_dump, sql_user, sql_pass

class Mode(Enum):
    Today = 0
    NewDay = 1
    NewWeek = 2
    NewMonth = 3
    NewYear = 4

mode_descr = {
    Mode.Today: 'новый архив дня',
    Mode.NewDay: 'архив нового дня',
    Mode.NewWeek: 'архив новой недели',
    Mode.NewMonth: 'архив нового месяца',
    Mode.NewYear: 'архив нового года'
    }

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

    mode = Mode.Today
    content = []
    case = 0

    def read_last(self):
        try:
            with open('last.txt', 'r') as f:
                self.last_backup_stamp = f.read()
        except FileNotFoundError:
            pass # Допустимая ситуация - считаем, что архивирование ещё ни разу не выполнялось

    def count_mode(self):
        self.last_backup_stamp = ''
        self.mode = Mode.Today
        self.read_last()
        if (self.last_backup_stamp == ''):
            return

        l = datetime.strptime(self.last_backup_stamp, '%Y-%m-%d %H:%M:%S.%f')
        n = datetime.now()
        if (n > l):
            if (n.year > l.year):
                self.mode = Mode.NewYear
            elif (n.month > l.month):
                self.mode = Mode.NewMonth
            elif (n.isocalendar()[1] > l.isocalendar()[1]):
                self.mode = Mode.NewWeek
            elif (n.day > l.day):
                self.mode = Mode.NewDay
    
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
        time.sleep(mail_wait)
        total = 0
        for file in fnmatch.filter(os.listdir('.'), 'HMBackup*.7z'):
            total += 1
            sz = os.path.getsize(file)
            self.content.append('   ' + file + '    ' + sizeof_fmt(sz))
            zf.write(file)
            os.remove(file)
        if (total == 0):
            raise BackupError('backup_mail', 'За назначенный таймаут файл архива не был получен.')

    def full_arch(self):
        return (self.mode == Mode.NewMonth) or (self.mode == Mode.NewYear)

    def archivate(self):
        if self.full_arch():
            dirs = full_dirs
        else:
            dirs = short_dirs

        try:
            os.mkdir('temp')
        except FileExistsError:
            pass

        fn = device + '-' + datetime.now().strftime('%Y.%m.%d-%H.%M.%S')
        zf = zipfile.ZipFile('temp/' + fn + '.zip', 'w')
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
        sz = os.path.getsize('temp/' + fn + '.zip')
        if (sz > 1000):
            self.content.append('   ' + fn + '.zip    ' + sizeof_fmt(sz))
        elif (sz == 0):
            raise BackupError('archivate', 'Не удалось создать архив ' + 'temp/' + fn + '.zip')
        else:
            raise BackupError('archivate', 'Пустой архив ' + 'temp/' + fn + '.zip')

    def rotate_dir(self, dir):
        if os.path.exists(dir):
            shutil.move(dir, dir+'_old')
        shutil.move('temp', dir)
        shutil.rmtree(dir+'_old', ignore_errors = True)
        self.content.append('Архив помещен в папку "{0}".'.format(dir))
    
    def rotate(self):
        if (self.mode == Mode.NewYear):
            self.rotate_dir('year')
        elif (self.mode == Mode.NewMonth):
            self.rotate_dir('month')
        elif (self.mode == Mode.NewWeek):
            self.rotate_dir('week')
        elif (self.mode == Mode.NewDay):
            self.rotate_dir('ystrd')
        else:
            self.rotate_dir('day')

    def add_info(self, src, dst):
        if (self.case == 0):
            self.case = 1
            self.content.append('  ' + src + ':')
        self.content.append('    ' + dst)
    
    def synch_dir(self, _src, _dst, _folder):
        #self.content.append('Синхронизация ' + _src + '\\' + _folder + ' -> ' + _dst + '\\' + _folder + ':')
        if (_src == 'nuc'):
            src = 'x:\\' + _folder
            dst = 'c:\\backup\\' + _folder
        else:
            src = 'c:\\backup\\' + _folder
            dst = 'x:\\' + _folder
    
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
    
            for f in files:
                fsrc = src + part + '\\' + f
                fdst = test + '\\' + f
                print(_dst + '\\' + _folder + part + '\\' + f, '...')
                if zzz or not os.path.exists(fdst):
                    shutil.copyfile(fsrc, fdst)
                    self.add_info(_src + '\\' + _folder + ' -> ' + _dst + '\\' + _folder, 'Файл скопирован в ' + _dst + '\\' + _folder + part + '\\' + f)
                else:
                    st = int(os.path.getmtime(fsrc))
                    dt = int(os.path.getmtime(fdst))
                    #print(st)
                    #print(dt)
                    if ((st - dt) > 5):
                        print('st:', st, 'dt:', dt)
                        shutil.copyfile(fsrc, fdst)
                        self.add_info(_src + '\\' + _folder + ' -> ' + _dst + '\\' + _folder, 'Файл обновлен в ' + _dst + '\\' + _folder + part + '\\' + f)
    
        if (self.case == 0):
            self.content.append('   ' + _src + '\\' + _folder + ' -> ' + _dst + '\\' + _folder + ' - без изменений.')

    def synch(self):
        if (device != 'Zen'):
            return
        self.content.append('')
        self.content.append('Синхронизация:')
        self.synch_dir('zen', 'nuc', 'zen')
        self.synch_dir('nuc', 'zen', 'nuc')
        self.synch_dir('zen', 'nuc', 'work')
        self.synch_dir('nuc', 'zen', 'work')
        self.synch_dir('zen', 'nuc', 'pipo')
        self.synch_dir('nuc', 'zen', 'pipo')

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

    def fix_time(self):
        with open('last.txt', 'w') as f:
            f.write(datetime.now().__str__())

    def save_log(self, input_wait, status, info):
        with open('backup.log', 'a') as f:
            f.write(str(datetime.now()) + '   ')
            f.write(status + ' ' + info + '\n')
        print(self.mode, mode_descr[self.mode])
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
            self.count_mode()
            self.archivate()
            self.rotate()
            self.synch()
            self.fix_time()
            self.save_log(input_wait, 'ok', '')
        except BackupError as be:
            self.save_log(input_wait, '[x]', str(be))
        except Exception as ex:
            self.save_log(input_wait, '[x]', str(ex))
            

if __name__ == '__main__':
    x = Backup()
    x.run(False)
