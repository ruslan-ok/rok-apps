import os, shutil
from django.contrib.auth.models import User
from task import const
from task.models import Task
from rusel.files import get_attach_path, storage_path

path = 'Z:\\apps\\docs'

class AttachChecker():
    def __init__(self):
        super().__init__()
        self.copied = []
        self.skipped = []

    def copy_attach(self, user, app, role, item, path, file):
        dest_path = get_attach_path(user, app, role, item.id, 3)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy(path + '\\' + file, dest_path)
        self.copied.append(dest_path + file)

    def copy_bill_attach(self, user, apart, year, month, path, file):
        if not apart:
            raise Exception('[x] Undefined apart: ' + path + '\\' + file)
        bill = None
        if month and Task.objects.filter(user=user.id, app_apart=const.NUM_ROLE_BILL, start__year=year, start__month=month, task_1=apart.id).exists():
            bill = Task.objects.filter(user=user.id, app_apart=const.NUM_ROLE_BILL, start__year=year, start__month=month, task_1=apart.id).get()
        if bill:
            dest_path = get_attach_path(user, const.APP_APART, const.ROLE_BILL, bill.id, 3)
        else:
            dest_path = storage_path.format(user.username) + 'attachments/' + const.APP_APART + '/' + apart.name + '/bill/' + str(year) + '/'
            if month:
                dest_path += str(month).zfill(2) + '/'
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy(path + '\\' + file, dest_path)
        self.copied.append(dest_path + file)

    def skip_attach(self, user, app, role, item_id, path, file):
        self.skipped.append(path + '\\' + file)

    def get_item(self, user, app, role, item_id):
        if not Task.objects.filter(id=item_id).exists():
            return None
        item = Task.objects.filter(id=item_id).get()
        matched = False
        match app:
            case const.APP_NOTE: 
                matched = (role == const.ROLE_NOTE and item.app_note == const.NUM_ROLE_NOTE)
            case const.APP_NEWS: 
                matched = (role == const.ROLE_NEWS and item.app_note == const.NUM_ROLE_NEWS)
            case const.APP_TODO: 
                matched = (role == const.ROLE_TODO and item.app_note == const.NUM_ROLE_TODO)
            case const.APP_STORE: 
                matched = (role == const.ROLE_STORE and item.app_note == const.NUM_ROLE_STORE)
            case const.APP_EXPEN: 
                matched = (role == const.ROLE_EXPENSE and item.app_note == const.NUM_ROLE_EXPENSE)
            case const.APP_HEALTH: 
                matched = (role == const.ROLE_INCIDENT and item.app_note == const.NUM_ROLE_INCIDENT)
            case const.APP_APART:
                match (role, item.app_apart):
                    case (const.ROLE_APART, const.NUM_ROLE_APART):
                        matched = True
                    case (const.ROLE_PRICE, const.NUM_ROLE_PRICE):
                        matched = True
                    case (const.ROLE_METER, const.NUM_ROLE_METER):
                        matched = True
                    case (const.ROLE_BILL, const.NUM_ROLE_BILL):
                        matched = True
            case const.APP_FUEL:
                match (role, item.app_fuel):
                    case (const.ROLE_CAR, const.NUM_ROLE_CAR):
                        matched = True
                    case (const.ROLE_PART, const.NUM_ROLE_PART):
                        matched = True
                    case (const.ROLE_SERVICE, const.NUM_ROLE_SERVICE):
                        matched = True
                    case (const.ROLE_FUEL, const.NUM_ROLE_FUEL):
                        matched = True
        if matched and (user.id == item.user.id):
            return item
        return None
        
    def scan_item_dir(self, user, app, role, item_id, dir):
        item = self.get_item(user, app, role, item_id)
        with os.scandir(dir) as files:
            for file in files:
                if file.is_dir():
                    raise Exception('Expected file, found directory: ' + dir + '\\' + file.name)
                if item:
                    self.copy_attach(user, app, role, item, dir, file.name)
                else:
                    self.skip_attach(user, app, role, item_id, dir, file.name)

    def scan_apart_bills_dir(self, user, apart, apart_dir):
        with os.scandir(apart_dir) as dirs:
            for dir in dirs:
                if not dir.is_dir():
                    raise Exception('Expected directory, found file: ' + apart_dir + '\\' + dir.name)
                year = int(dir.name)
                if (year < 2008) or (year > 2022):
                    raise Exception('Unexpected year value: ' + apart_dir + '\\' + dir.name)
                with os.scandir(apart_dir + '\\' + dir.name) as items:
                    for item in items:
                        if not item.is_dir():
                            self.copy_bill_attach(user, apart, year, None, apart_dir + '\\' + dir.name, item.name)
                        else:
                            if ' ' in item.name:
                                month = int(item.name.split(' ')[0])
                            else:
                                month = int(item.name)
                            if (month < 1) or (month > 12):
                                raise Exception('Wrong month number: ' + apart_dir + '\\' + dir.name + '\\' + item.name)
                            with os.scandir(apart_dir + '\\' + dir.name + '\\' + item.name) as files:
                                for file in files:
                                    if file.is_dir():
                                        raise Exception('Expected file, found directory: ' + apart_dir + '\\' + dir.name + '\\' + item.name + '\\' + file.name)
                                    self.copy_bill_attach(user, apart, year, month, apart_dir + '\\' + dir.name + '\\' + item.name, file.name)

    def scan_app_dir(self, user, app, app_dir):
        with os.scandir(app_dir) as dirs:
            for dir in dirs:
                if not dir.is_dir():
                    raise Exception('Expected directory, found file: ' + app_dir + '\\' + dir.name)
                if not '_' in dir.name:
                    raise Exception('Expected symbol "_" in directory name: ' + app_dir + '\\' + dir.name)
                role_name = dir.name.split('_')[0]
                item_id = int(dir.name.split('_')[1])
                role = None
                match (app, role_name):
                    case (const.APP_APART, 'apart'):
                        role = const.ROLE_APART
                    case (const.APP_APART, 'bill'):
                        role = const.ROLE_BILL
                    case (const.APP_APART, 'meter'):
                        role = const.ROLE_METER
                    case (const.APP_APART, 'price'):
                        role = const.ROLE_PRICE
                    case (const.APP_APART, 'service'):
                        role = const.ROLE_SERVICE
                    case (const.APP_EXPEN, 'expense'):
                        role = const.ROLE_EXPENSE
                    case (const.APP_FUEL, 'car'):
                        role = const.ROLE_CAR
                    case (const.APP_FUEL, 'fuel'):
                        role = const.ROLE_FUEL
                    case (const.APP_FUEL, 'part'):
                        role = const.ROLE_PART
                    case (const.APP_FUEL, 'service'):
                        role = const.ROLE_SERVICE
                    case (const.APP_NEWS, 'news'):
                        role = const.ROLE_NEWS
                    case (const.APP_NOTE, 'note'):
                        role = const.ROLE_NOTE
                    case (const.APP_STORE, 'store'):
                        role = const.ROLE_STORE
                    case (const.APP_TODO, 'task'):
                        role = const.ROLE_TODO
                    case (const.APP_TODO, 'todo'):
                        role = const.ROLE_TODO
                    case (const.APP_HEALTH, 'incident'):
                        role = const.ROLE_INCIDENT
                if not role:
                    raise Exception('Undefined role for app "' + app + '", role_name "' + role_name + '"')

                if (app == const.APP_APART) and (role == const.ROLE_APART) and (item_id in (1,2,3)):
                    apart = Task.objects.filter(app_apart=const.NUM_ROLE_APART, src_id=item_id).get()
                    self.scan_apart_bills_dir(user, apart, app_dir + '\\' + dir.name)
                else:
                    self.scan_item_dir(user, app, role, item_id, app_dir + '\\' + dir.name)

    def scan_attach_dir(self, user, attach_dir):
        with os.scandir(attach_dir) as dirs:
            for dir in dirs:
                if not dir.is_dir():
                    raise Exception('Expected directory, found file: ' + attach_dir + '\\' + dir.name)
                app = None
                match dir.name:
                    case 'apart':
                        app = const.APP_APART
                    case 'expen':
                        app = const.APP_EXPEN
                    case 'fuel':
                        app = const.APP_FUEL
                    case 'news':
                        app = const.APP_NEWS
                    case 'note':
                        app = const.APP_NOTE
                    case 'store':
                        app = const.APP_STORE
                    case 'todo':
                        app = const.APP_TODO
                    case 'health':
                        app = const.APP_HEALTH
                if not app:
                    raise Exception('Expected application name, found: ' + attach_dir + '\\' + dir.name)
                self.scan_app_dir(user, app, attach_dir + '\\' + dir.name)

    def scan_user_dir(self, user, user_dir):
        with os.scandir(user_dir) as dirs:
            for dir in dirs:
                if (dir.name == 'attachments'):
                    self.scan_attach_dir(user, user_dir + '\\' + dir.name)

    def convert_users(self):
        with os.scandir(path) as users_level:
            for user_dir in users_level:
                if user_dir.name == 'Thumbs.db':
                    continue
                if not user_dir.is_dir():
                    raise Exception('[x] expected directory, found file: ' + path + '\\' + user_dir.name)
                if user_dir.name == 'version':
                    continue
                if '_' not in user_dir.name:
                    raise Exception('[x] expected symbol "_" in directory name: ' + path + '\\' + user_dir.name)
                prefix = user_dir.name.split('_')[0]
                user_id = int(user_dir.name.split('_')[1])
                if (prefix != 'user'):
                    raise Exception('[x] expected prefix "user_" in directory name: ' + path + '\\' + user_dir.name)
                user = User.objects.filter(id=user_id).get()
                self.scan_user_dir(user, path + '\\' + user_dir.name)

def convert_attach():
    converter = AttachChecker()
    try:
        converter.convert_users()
        return {
            'result': 'ok', 
            'tot_src': len(converter.copied) + len(converter.skipped),
            'tot_copied': len(converter.copied),
            'tot_skipped': len(converter.skipped),
            'copied': converter.copied,
            'skipped': converter.skipped,
        }
    except Exception as e:
        return {'error': str(e)}
