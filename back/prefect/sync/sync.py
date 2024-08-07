import requests, json, paramiko, os
from pathlib import Path, WindowsPath
from prefect import flow, task
from pydantic import BaseModel
from datetime import datetime
from enum import Enum
from sync_params import (
    HUGE_SIZE_LIMIT,
    MAX_FILES_TO_SYNC,
    SyncEntry,
    sync_entries,
    get_dir_api,
    modify_mt_api,
    headers,
    verify
)

class SyncAction(Enum):
    RemoveLocal = 1
    RemoveRemote = 2
    Upload = 3
    Download = 4
    SetTimeLocal = 5
    SetTimeRemote = 6

STAT_LABEL = {
    SyncAction.RemoveLocal: 'remove locally',
    SyncAction.RemoveRemote: 'remove remotely',
    SyncAction.Upload: 'upload to the server',
    SyncAction.Download: 'download from the server',
    SyncAction.SetTimeLocal: 'set time local',
    SyncAction.SetTimeRemote: 'set time remote',
}

TASK_PREFIX = {
    SyncAction.RemoveLocal: 'Remove local',
    SyncAction.RemoveRemote: 'Remove remote',
    SyncAction.Upload: 'Upload',
    SyncAction.Download: 'Download',
    SyncAction.SetTimeLocal: 'Set time local',
    SyncAction.SetTimeRemote: 'Set time remote',
}

SECONDS_IN_DAY = 24 * 60 * 60

class FileSutatus(Enum):
    Unknown = 0
    Correct = 1
    Copy = 2
    Remove = 3
    Rewrite = 4
    SetTime = 5

def size_fmt(num):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return f'{num:3.1f}{unit}b'
        num /= 1024.0
    return f'{num:.1f}YiB'

class FileInfo(BaseModel):
    status: FileSutatus
    entry: SyncEntry
    folder: str
    name: str
    date_time: datetime
    size: int

    @property
    def local_file(self) -> WindowsPath:
        return WindowsPath(self.entry.local) / self.folder / self.name

    @property
    def remote_file(self) -> Path:
        return Path(self.entry.remote) / self.folder / self.name
    
    @property
    def local_path(self) -> str:
        return str(self.local_file)
    
    @property
    def remote_path(self) -> str:
        return self.remote_file.as_posix()
    
    @property
    def relative_path(self):
        return self.folder + '/' + self.name
    
    @property
    def size_fmt(self):
        return size_fmt(self.size)

class Sync():

    @task(tags=['sync', 'open'])
    def open(self):
        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            client.connect('rok-apps.com', username='ruslan')
            self.sftp = client.open_sftp()
            return True
        except Exception as e:
            print(f'An error occurred: {e}')
            return False
        
    def close(self):
        self.sftp.close()

    @flow
    def sync_with_server(self):
        if not self.open():
            return
        self.local = {}
        self.remote = {}
        self.cur_folder = []
        self.dirs = []
        self.fill_local()
        self.fill_remote()
        self.count_status()
        self.do_sync()
        self.close()

    @task(tags=['sync', 'fill', 'local'])
    def fill_local(self):
        for entry in sync_entries:
            for dirname, _, files in WindowsPath(entry.local).walk():
                for filename in files:
                    if filename == 'Thumbs.db':
                        continue
                    file = dirname / filename
                    mt = file.stat().st_mtime
                    dttm = datetime.fromtimestamp(mt)
                    dttm = datetime.strptime(dttm.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                    sz = file.stat().st_size
                    x = FileInfo(
                        status=FileSutatus.Unknown,
                        entry=entry,
                        folder=dirname.relative_to(WindowsPath(entry.local)).as_posix(),
                        name=filename,
                        date_time=dttm,
                        size=sz,
                    )
                    self.local[x.relative_path] = x
    
    @task(tags=['sync', 'fill', 'remote'])
    def fill_remote(self):
        for entry in sync_entries:
            resp = requests.get(get_dir_api + '?folder=' + entry.remote, headers=headers, verify=verify)
            if (resp.status_code != 200):
                print('[ERROR] api_call: Status = ' + str(resp.status_code) + '. ' + str(resp.content))
            else:
                ret = json.loads(resp.content)
                for fi in ret['file_list']:
                    x = FileInfo(
                        status=FileSutatus.Unknown,
                        entry=entry,
                        folder=fi['folder'],
                        name=fi['name'],
                        date_time=datetime.strptime(fi['date_time'], '%Y-%m-%dT%H:%M:%S'),
                        size=fi['size'],
                    )
                    self.remote[x.relative_path] = x
    
    @task(tags=['sync', 'count'])
    def count_status(self):
        for k in self.remote.keys():
            r = self.remote[k]
            if k in self.local:
                l = self.local[k]
                if r.size == l.size and r.date_time == l.date_time:
                    r.status = FileSutatus.Correct
                    l.status = FileSutatus.Correct
                elif r.date_time == l.date_time:
                    if r.size > l.size:
                        r.status = FileSutatus.Copy
                        l.status = FileSutatus.Rewrite
                    else:
                        r.status = FileSutatus.Rewrite
                        l.status = FileSutatus.Copy
                elif r.size == l.size:
                    if r.date_time > l.date_time:
                        r.status = FileSutatus.Rewrite
                        l.status = FileSutatus.SetTime
                    else:
                        r.status = FileSutatus.SetTime
                        l.status = FileSutatus.Rewrite
                else:
                    if r.size > l.size and r.date_time > l.date_time:
                        r.status = FileSutatus.Copy
                        l.status = FileSutatus.Rewrite
                    elif r.size < l.size and r.date_time < l.date_time:
                        r.status = FileSutatus.Rewrite
                        l.status = FileSutatus.Copy
                    else:
                        raise Exception('Check!')

                if r.status == FileSutatus.Copy and l.status == FileSutatus.Rewrite and l.folder.startswith('vivo'):
                    r.status = FileSutatus.Rewrite
                    l.status = FileSutatus.Copy

                if r.status == FileSutatus.Rewrite and l.status == FileSutatus.Copy and r.folder.startswith('nuc'):
                    r.status = FileSutatus.Copy
                    l.status = FileSutatus.Rewrite

        for k in self.remote.keys():
            r = self.remote[k]
            if r.status == FileSutatus.Unknown or l.status == 0:
                if r.folder.startswith('vivo'):
                    r.status = FileSutatus.Remove
                else:
                    r.status = FileSutatus.Copy

        for k in self.local.keys():
            l = self.local[k]
            if l.status == FileSutatus.Unknown or l.status == 0:
                if l.folder.startswith('nuc'):
                    l.status = FileSutatus.Remove
                else:
                    l.status = FileSutatus.Copy
    
    def remove_local(self, f: FileInfo):
        f.local_file.unlink()

    def remove_remote(self, f: FileInfo):
        self.sftp.remove(f.remote_path)

    def mkdir_p(self, remote_directory):
        dir_path = str()
        for dir_folder in remote_directory.split("/"):
            if dir_folder == "":
                continue
            dir_path += f'/{dir_folder}'
            try:
                self.sftp.listdir(dir_path)
            except IOError:
                self.sftp.mkdir(dir_path)

    def upload_file(self, f: FileInfo):
        if f.size > HUGE_SIZE_LIMIT:
            return
        self.mkdir_p(f'{f.entry.remote}/{f.folder}')
        self.sftp.put(f.local_path, f.remote_path)
        self.set_time_remote(f)

    def download_file(self, f: FileInfo):
        if f.size > HUGE_SIZE_LIMIT:
            return
        os.makedirs(f'{f.entry.local}/{f.folder}', exist_ok=True)
        self.sftp.get(f.remote_path, f.local_path)
        self.set_time_local(f)

    def set_time_remote(self, f: FileInfo):
        mod_time = f.date_time.strftime('%Y-%m-%dT%H:%M:%S')
        params = f'?path={f.remote_path}&mod_time={mod_time}'
        resp = requests.get(modify_mt_api + params, headers=headers, verify=verify)
        if (resp.status_code != 200):
            print('[ERROR] modify_mt_api: Status = ' + str(resp.status_code) + '. ' + str(resp.content))

    def set_time_local(self, f: FileInfo):
        dt_epoch = f.date_time.timestamp()
        os.utime(f.local_path, (dt_epoch, dt_epoch))
    
    def print_stat(self, action: SyncAction, items, control_status):
        sizes = [items[x].size for x in items.keys() if items[x].status == control_status]
        print(f'- Files to {STAT_LABEL[action]}: {len(sizes)} [{size_fmt(sum(sizes))}]')

    @task(task_run_name='{name}', tags=['sync', 'file'])
    def sync_file(self, name: str, action: SyncAction, f: FileInfo):
        match action:
            case SyncAction.RemoveLocal: self.remove_local(f)
            case SyncAction.RemoveRemote: self.remove_remote(f)
            case SyncAction.Upload: self.upload_file(f)
            case SyncAction.Download: self.download_file(f)
            case SyncAction.SetTimeLocal: self.set_time_local(f)
            case SyncAction.SetTimeRemote: self.set_time_remote(f)

    @task(task_run_name='Set all time local', tags=['sync', 'time', 'local'])
    def set_all_time_local(self, files):
        for f in files:
            self.set_time_local(f)
 
    @task(task_run_name='Set all time remote', tags=['sync', 'time', 'remote'])
    def set_all_time_remote(self, files):
        for f in files:
            self.set_time_remote(f)
    
    def transliterate(self, name):
        """
        Автор: LarsKort
        Дата: 16/07/2011; 1:05 GMT-4;
        Не претендую на "хорошесть" словарика. В моем случае и такой пойдет,
        вы всегда сможете добавить свои символы и даже слова. Только
        это нужно делать в обоих списках, иначе будет ошибка.
        """
        # Слоаврь с заменами
        slovar = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'jo',
            'ж':'zh','з':'z','и':'i','й':'i','к':'k','л':'l','м':'m','н':'n',
            'о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h',
            'ц':'c','ч':'ch','ш':'sh','щ':'sch','ъ':'','ы':'y','ь':'','э':'e',
            'ю':'ju','я':'ja', 'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'JO',
            'Ж':'ZH','З':'Z','И':'I','Й':'I','К':'K','Л':'L','М':'M','Н':'N',
            'О':'O','П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F','Х':'H',
            'Ц':'C','Ч':'CH','Ш':'SH','Щ':'SCH','Ъ':'','Ы':'Y','Ь':'','Э':'E',
            'Ю':'U','Я':'JA',
            '№':'N','ą':'ou','Ą':'OU','ć':'c','Ć':'C','ę':'en','Ę':'EN',
            'ł':'l','Ł':'L','ń':'n','Ń':'N','ó':'u','Ó':'U','ś':'s','Ś':'S',
            'ż':'zh','Ż':'ZH','ź':'z','Ź':'Z',
            'ґ':'','ї':'', 'є':'','Ґ':'g','Ї':'i',
            'Є':'e'}
            
        # Циклически заменяем все буквы в строке
        for key in slovar:
            name = name.replace(key, slovar[key])
        return name

    def get_task_name(self, action: SyncAction, f: FileInfo):
        result = f'{TASK_PREFIX[action]}: {f.folder}/{f.name} [{f.size_fmt}]'
        result = self.transliterate(result)
        if f.size > HUGE_SIZE_LIMIT:
            result = 'Skip ' + result
        return result

    def run_sync_file(self, action: SyncAction, f: FileInfo):
        name = self.get_task_name(action, f)
        self.sync_file(name, action, f)
        self.counter += 1

    @flow(log_prints=True)
    def do_sync(self):
        print('Statistics before starting synchronization:')
        self.print_stat(SyncAction.RemoveLocal, self.local, FileSutatus.Remove)
        self.print_stat(SyncAction.RemoveRemote, self.remote, FileSutatus.Remove)
        self.print_stat(SyncAction.Upload, self.local, FileSutatus.Copy)
        self.print_stat(SyncAction.Download, self.remote, FileSutatus.Copy)
        self.print_stat(SyncAction.SetTimeLocal, self.remote, FileSutatus.SetTime)
        self.print_stat(SyncAction.SetTimeRemote, self.local, FileSutatus.SetTime)
        self.counter = 0

        files = [self.remote[x] for x in self.remote.keys() if self.remote[x].status == FileSutatus.SetTime]
        if files:
            self.set_all_time_local(files)

        files = [self.local[x] for x in self.local.keys() if self.local[x].status == FileSutatus.SetTime]
        if files:
            self.set_all_time_remote(files)

        for k in self.local.keys():
            f = self.local[k]
            match f.status:
                case FileSutatus.Remove: self.run_sync_file(SyncAction.RemoveLocal, f)
                case FileSutatus.Copy: self.run_sync_file(SyncAction.Upload, f)
            if self.counter >= MAX_FILES_TO_SYNC:
                break
        for k in self.remote.keys():
            f = self.remote[k]
            match f.status:
                case FileSutatus.Remove: self.run_sync_file(SyncAction.RemoveRemote, f)
                case FileSutatus.Copy: self.run_sync_file(SyncAction.Download, f)
            if self.counter >= MAX_FILES_TO_SYNC:
                break

if __name__ == '__main__':
    z = Sync()
    z.sync_with_server()
