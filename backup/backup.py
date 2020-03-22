import sys
from datetime import datetime
from enum import Enum
import smtplib
from email.message import EmailMessage
import os
import zipfile
import math
import subprocess
import time
import fnmatch
import shutil

from secret import device, mail_login, mail_pass, mail_from, mail_to, mail_wait, short_dirs, full_dirs, sql_dump, sql_user, sql_pass


class Status(Enum):
    Ok = 0
    Error = 1

status_descr = {
    Status.Ok: '[Ok]',
    Status.Error: '[Error]',
    }

class Mode(Enum):
    FirstArch = 0
    NewDay = 1
    NewWeek = 2
    NewMonth = 3
    NewYear = 4

mode_descr = {
    Mode.FirstArch: 'новый архив дня',
    Mode.NewDay: 'архив нового дня',
    Mode.NewWeek: 'архив новой недели',
    Mode.NewMonth: 'архив нового месяца',
    Mode.NewYear: 'архив нового года'
    }

def send_email(status, text, errors):
    s = smtplib.SMTP(host='rusel.by', port=25)
    s.starttls()
    s.login(mail_login, mail_pass)
    msg = EmailMessage()
    msg['From'] = mail_from
    msg['To'] = mail_to
    msg['Subject']='Архивация на ' + device + ' - ' + status_descr[status]
    content = ''
    for str in text:
        content = content + str + '\n'
    if (len(errors) > 0):
        content = content + '\nОшибки:\n'
        for str in errors:
            content = content + '   ' + str + '\n'
    msg.set_content(content)
    s.send_message(msg)
    del msg
    s.quit()

def save_now():
    f = open('last.txt', 'w')
    f.write(datetime.now().__str__())
    f.close()


def sizeof_fmt(num, suffix = 'B'):
    magnitude = int(math.floor(math.log(num, 1024)))
    val = num / math.pow(1024, magnitude)
    if magnitude > 7:
        return '{:.1f}{}{}'.format(val, 'Y', suffix)
    return '{:3.1f}{}{}'.format(val, [' ', ' K', ' M', ' G', ' T', ' P', ' E', ' Z'][magnitude], suffix)
    

def backup_db(zf, content, errors):
    file = 'mysql_backup.sql'
    try:
        return_code = subprocess.call('"' + sql_dump + '"  --all-databases --user=' + sql_user + ' --password=' + sql_pass + ' --result-file=' + file, shell = True)
    except:
        errors.append('Ошибка создания бэкапа mysql: ошибка вызова процесса.')
        errors.append(sys.exc_info()[0])
        return Status.Error

    if (return_code != 0):
        errors.append('Ошибка создания бэкапа mysql: ' + return_code.__str__())
        return Status.Error
    sz = os.path.getsize(file)
    content.append('   ' + file + '    ' + sizeof_fmt(sz))
    zf.write(file)
    os.remove(file)
    return Status.Ok


def backup_mail(zf, content, errors):
    try:
        return_code = subprocess.call('MailBackup.vbs', shell = True)
    except:
        errors.append('Ошибка создания бэкапа почты: ошибка вызова процесса.')
        errors.append(sys.exc_info()[0])
        return Status.Error

    if (return_code != 0):
        errors.append('Ошибка создания бэкапа почты: ' + return_code.__str__())
        return Status.Error
    time.sleep(mail_wait)
    total = 0
    for file in fnmatch.filter(os.listdir('.'), 'HMBackup*.7z'):
        total += 1
        sz = os.path.getsize(file)
        content.append('   ' + file + '    ' + sizeof_fmt(sz))
        zf.write(file)
        os.remove(file)
    if (total == 0):
        errors.append('Ошибка создания бэкапа почты: за назначенный таймаут файл архива не был получен.')
        return Status.Error
    return Status.Ok


def archivate(mode, content, errors):
    print(mode)

    if (mode == Mode.NewMonth) or (mode == Mode.NewYear):
        dirs = full_dirs
    else:
        dirs = short_dirs

    try:
        os.mkdir('temp')
    except FileExistsError:
        pass
    except:
        errors.append('Не удалось создать каталог temp')
        errors.append(sys.exc_info()[0])
        return Status.Error

    try:
        fn = device + '-' + datetime.now().strftime('%Y.%m.%d-%H.%M.%S')
        zf = zipfile.ZipFile('temp/' + fn + '.zip', 'w')
        status = Status.Ok
        for dir in dirs:
            print('Archiving:', dir, '...')
            if (dir == 'mysql'):
                status = backup_db(zf, content, errors)
            elif (dir == 'email'):
                status = backup_mail(zf, content, errors)
            else:
                for dirname, subdirs, files in os.walk(dir):
                    zf.write(dirname)
                    for filename in files:
                        zf.write(os.path.join(dirname, filename))
        zf.close()
        sz = os.path.getsize('temp/' + fn + '.zip')
        if (sz > 1000):
            content.append('   ' + fn + '.zip    ' + sizeof_fmt(sz))
            return status
        elif (sz == 0):
            errors.append('Не удалось создать архив ' + 'temp/' + fn + '.zip')
            return Status.Error
        else:
            errors.append('Пустой архив ' + 'temp/' + fn + '.zip')
            return Status.Error
    except:
        errors.append('Необработанная ошибка при архивации')
        errors.append(sys.exc_info()[0])
        return Status.Error

def rotate(mode, content, errors):
    try:
        if (mode != Mode.NewMonth) and (mode != Mode.NewYear):
            shutil.rmtree('day', ignore_errors = True)
            shutil.move('temp', 'day')

        if (mode == Mode.NewYear):
            shutil.move('temp', 'year')
            content.append('Архив помещен в папку "year".')
        elif (mode == Mode.NewMonth):
            shutil.rmtree('month', ignore_errors = True)
            shutil.move('temp', 'month')
            content.append('Архив помещен в папку "month".')
        elif (mode == Mode.NewWeek):
            shutil.rmtree('week', ignore_errors = True)
            shutil.move('temp', 'week')
            content.append('Архив помещен в папки "day" и "week".')
        elif (mode == Mode.NewDay):
            shutil.rmtree('ystrd', ignore_errors = True)
            shutil.move('temp', 'ystrd')
            content.append('Архив помещен в папки "day" и "ystrd".')
        else:
            content.append('Архив помещен в папку "day".')
        return Status.Ok
    except:
        errors.append('Ошибка при перемещении архива на текущем устройстве.')
        errors.append(sys.exc_info()[0])
        return Status.Error


def main():
    mode = Mode.FirstArch
    try:
        f = open('last.txt', 'r')
        s = f.read()
        f.close()
        l = datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f')
        n = datetime.now()
        if (n > l):
            if (n.year > l.year):
                mode = Mode.NewYear
            elif (n.month > l.month):
                mode = Mode.NewMonth
            elif (n.isocalendar()[1] > l.isocalendar()[1]):
                mode = Mode.NewWeek
            elif (n.day > l.day):
                mode = Mode.NewDay
    except FileNotFoundError:
        pass

    content = ['Устройство: ' + device]
    content.append('Тип: ' + mode_descr[mode])
    errors = []
    status = archivate(mode, content, errors)
    if (status == Status.Ok):
        status = rotate(mode, content, errors)
    save_now()
    send_email(status, content, errors)
    print(status)
    if (status == Status.Error):
        for er in errors:
            print(er)
    else:
        for ct in content:
            print(ct)


try:
    if __name__ == '__main__':
        main()
except:
    input(sys.exc_info()[0])

