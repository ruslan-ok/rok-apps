import os, requests
import shutil
from datetime import datetime
from ftplib import FTP
from enum import Enum
from logs.models import EventType

FTP_SIZE_LIMIT = 50000000

class FileSutatus(Enum):
    Unknown = 0
    Correct = 1
    Copy = 2
    Remove = 3
    Rewrite = 4

class Sync():

    def __init__(self, log):
        self.log = log
        self.this_device = os.environ.get('DJANGO_DEVICE')
        self.host = os.environ.get('DJANGO_HOST_FTP')
        self.user = os.environ.get('DJANGO_FTP_USER')
        self.pwrd = os.environ.get('DJANGO_FTP_PWRD')
        work_dir = os.environ.get('DJANGO_BACKUP_FOLDER')
        self.work_dir = '/'.join(work_dir.replace('\\', ' ').split())
        self.nuc_drive = os.environ.get('DJANGO_BACKUP_NUC', '')
        self.api_url = 'https://rusel.by/api/groups/ftp_mfmt/'
        service_token = os.environ.get('DJANGO_SERVICE_TOKEN')
        self.headers = {'Authorization': 'Token ' + service_token, 'User-Agent': 'Mozilla/5.0'}
        self.verify = os.environ.get('DJANGO_CERT')

    def run(self):
        self.log(EventType.INFO, 'method', '+Synch.run() started')
        print('- run')
        if self.this_device == 'Vivo':
            self.local = []
            self.remote = []
            self.cur_folder = []
            self.dirs = []
            self.fill_locale(self.work_dir)
            self.fill_remote()
            self.count_status()
            self.do_sync()
        print('* run')
        self.log(EventType.INFO, 'method', '-Synch.run() finished')

    def fill_locale(self, root_dir):
        print('- fill_locale')
        for dirname, subdirs, files in os.walk(root_dir):
            dirname = dirname.replace(root_dir, '')
            if dirname:
                dirname = dirname.replace('\\', '/')[1:]
            fpath = os.path.join(root_dir, dirname).replace('\\', '/')
            for filename in files:
                fullname = os.path.join(fpath, filename).replace('\\', '/')
                mt = os.path.getmtime(fullname)
                dttm = datetime.fromtimestamp(mt)
                dttm = datetime.strptime(dttm.strftime('%m-%d-%Y %I:%M%p'), '%m-%d-%Y %I:%M%p')
                sz = os.path.getsize(fullname)
                self.local.append({
                    'status': FileSutatus.Unknown,
                    'folder': dirname,
                    'name': filename,
                    'date_time': dttm,
                    'size': sz,
                })
    
    def fill_remote(self):
        print('- fill_remote')
        if os.path.exists(self.nuc_drive):
            self.fill_locale(self.nuc_drive)
        else:
            with FTP(self.host, self.user, self.pwrd, encoding='windows-1251') as ftp:
                self.scan_remote(ftp, '.')
    
    def count_status(self):
        print('- count_status')
        self.drive_folder('nuc', is_remote=True)
        self.drive_folder('vivo', is_remote=False)
        rem_files = [d for d in self.remote if not (d['folder'].startswith('nuc') or d['folder'].startswith('vivo'))]
        loc_files = [d for d in self.local if not (d['folder'].startswith('nuc') or d['folder'].startswith('vivo'))]
        for r in rem_files:
            for l in loc_files:
                if r['folder'] == l['folder'] and r['name'] == l['name']:
                    if r['date_time'] == l['date_time'] and r['size'] == l['size']:
                        r['status'] = FileSutatus.Correct
                        l['status'] = FileSutatus.Correct
                    elif r['date_time'] == l['date_time'] or r['date_time'] > l['date_time']:
                        if r['size'] > l['size']:
                            r['status'] = FileSutatus.Copy
                            l['status'] = FileSutatus.Rewrite
                        else:
                            r['status'] = FileSutatus.Rewrite
                            l['status'] = FileSutatus.Copy
        for x in rem_files:
            if x['status'] == FileSutatus.Unknown:
                x['status'] = FileSutatus.Copy
        for x in loc_files:
            if x['status'] == FileSutatus.Unknown:
                x['status'] = FileSutatus.Copy
    
    def drive_folder(self, name, is_remote):
        if is_remote:
            etalon = [d for d in self.remote if d['folder'].startswith(name)]
            backup = [d for d in self.local if d['folder'].startswith(name)]
        else:
            etalon = [d for d in self.local if d['folder'].startswith(name)]
            backup = [d for d in self.remote if d['folder'].startswith(name)]
        for e in etalon:
            for b in backup:
                if e['folder'] == b['folder'] and e['name'] == b['name']:
                    if e['date_time'] == b['date_time'] and e['size'] == b['size']:
                        e['status'] = FileSutatus.Correct
                        b['status'] = FileSutatus.Correct
                    else:
                        b['status'] = FileSutatus.Rewrite
        for e in etalon:
            if e['status'] != FileSutatus.Correct:
                e['status'] = FileSutatus.Copy
        for b in backup:
            if b['status'] != FileSutatus.Correct and b['status'] != FileSutatus.Rewrite:
                b['status'] = FileSutatus.Remove

    def get_full_local_name(self, x):
        fpath = os.path.join(self.work_dir, x["folder"])
        fullname = os.path.join(fpath, x["name"])
        return fullname

    def get_mapped_local_name(self, x):
        fpath = os.path.join(self.nuc_drive, x["folder"])
        fullname = os.path.join(fpath, x["name"])
        return fullname

    def get_file_path(self, x):
        return f'{x["folder"]}/{x["name"]}'

    def remove_locale(self, x):
        os.remove(self.get_full_local_name(x))
        self.log(EventType.INFO, 'deleted local', self.get_file_path(x))

    def remove_remote(self, x):
        if os.path.exists(self.nuc_drive):
            os.remove(self.get_mapped_local_name(x))
        else:
            with FTP(self.host, self.user, self.pwrd, encoding='windows-1251') as ftp:
                ftp.cwd(x['folder'])
                ftp.delete(x['name'])
        self.log(EventType.INFO, 'deleted remote', self.get_file_path(x))

    def upload_file(self, x):
        fsrc = self.get_full_local_name(x)
        if os.path.exists(self.nuc_drive):
            fdst = self.get_mapped_local_name(x)
            shutil.copyfile(fsrc, fdst)
            dt_epoch = x['date_time'].timestamp()
            os.utime(fdst, (dt_epoch, dt_epoch))
            self.log(EventType.INFO, 'copied local -> remote', self.get_file_path(x))
        else:
            if x['size'] > FTP_SIZE_LIMIT:
                self.log(EventType.INFO, 'skipped big local -> remote', self.get_file_path(x))
            else:
                with FTP(self.host, self.user, self.pwrd, encoding='windows-1251') as ftp, open(fsrc, 'rb') as file:
                    print(f'FTP <- : {x["folder"]}/{x["name"]} [{x["size"]}]')
                    ftp.cwd(x['folder'])
                    ftp.storbinary(f'STOR {x["name"]}', file)
                    print('done')
                mod_time = x['date_time'].strftime('%m-%d-%Y %I:%M%p')
                params = f'?folder={x["folder"]}&file={x["name"]}&mod_time={mod_time}'
                requests.get(self.api_url + params, headers=self.headers, verify=self.verify)
                self.log(EventType.INFO, 'copied local -> remote', self.get_file_path(x))

    def download_file(self, x):
        fdst = self.get_full_local_name(x)
        if os.path.exists(self.nuc_drive):
            fsrc = self.get_mapped_local_name(x)
            shutil.copyfile(fsrc, fdst)
            dt_epoch = x['date_time'].timestamp()
            os.utime(fdst, (dt_epoch, dt_epoch))
            self.log(EventType.INFO, 'copied local <- remote', self.get_file_path(x))
        else:
            if x['size'] > FTP_SIZE_LIMIT:
                self.log(EventType.INFO, 'skipped big local <- remote', self.get_file_path(x))
            else:
                with FTP(self.host, self.user, self.pwrd, encoding='windows-1251') as ftp, open(fdst, 'rb') as file:
                    print(f'FTP -> : {x["folder"]}/{x["name"]} [{x["size"]}]')
                    ftp.cwd(x['folder'])
                    ftp.retrbinary(f'RETR {x["name"]}', file.write)
                    print('done')
                dt_epoch = x['date_time'].timestamp()
                os.utime(fdst, (dt_epoch, dt_epoch))
                self.log(EventType.INFO, 'copied local <- remote', self.get_file_path(x))

    def do_sync(self):
        print('- do_sync')
        for x in self.local:
            match x['status']:
                case FileSutatus.Remove: self.remove_locale(x)
                case FileSutatus.Copy: self.upload_file(x)
        for x in self.remote:
            match x['status']:
                case FileSutatus.Remove: self.remove_remote(x)
                case FileSutatus.Copy: self.download_file(x)
    
    def scan_remote(self, ftp, dir):
        self.cur_folder = []
        self.cur_dir = '' if dir == '.' else dir
        ftp.dir(dir, self.dir_callback)
        for x in self.cur_folder:
            if not x['is_dir']:
                self.remote.append({
                    'status': FileSutatus.Unknown,
                    'folder': x['folder'],
                    'name': x['name'],
                    'date_time': x['date_time'],
                    'size': x['size'],
                })
            if x['is_dir']:
                if dir == '.':
                    next_dir = x['name']
                else:
                    next_dir = dir + '/' + x['name']
                self.dirs.append(next_dir)
        while len(self.dirs):
            next = self.dirs.pop(0)
            self.scan_remote(ftp, next)

    def dir_callback(self, line):
        parts = line.split()
        f_dt = parts[0]
        f_tm = parts[1]
        f_sz = parts[2]
        work = ' '.join(parts)
        info = ' '.join(parts[:3])
        name = work.replace(info + ' ', '')
        is_dir = (f_sz == '<DIR>')
        size = None if is_dir else int(f_sz)
        dt_tm = datetime.strptime(f_dt + ' ' + f_tm, '%m-%d-%Y %I:%M%p')
        self.cur_folder.append({
            'folder': self.cur_dir,
            'name': name,
            'is_dir': is_dir,
            'date_time': dt_tm,
            'size': size,
        })

# if __name__ == '__main__':
#     z = Sync()
#     z.run()
