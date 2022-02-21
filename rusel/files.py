import os
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from task import const
from task.models import Task
from rusel.secret import storage_dvlp, storage_prod, service_dvlp, service_prod, folder_dvlp, folder_prod
from apart.forms.price import APART_SERVICE

folder_path  = folder_dvlp
storage_path = storage_dvlp
service_path = service_dvlp

file_storage_url = 'doc/'
    
FILE_DESIGN = [
    'Brown',
    'Chocolate',
    'BlueViolet',
    'CadetBlue',
    'Blue',
    'CornflowerBlue',
    'Crimson',
    'DarkBlue',
    'DarkCyan',
    'DarkGoldenRod',
    'DarkGreen',
    'DarkMagenta',
    'DarkOliveGreen',
    'DarkOrchid',
    'DarkRed',
    'DarkSlateBlue',
    'Grey',
    'DarkSlateGray',
    'Indigo',
    'MidnightBlue',
    'Maroon',
    'RoyalBlue',
    'Green',
    'Gold',
    'Teal',
    'SteelBlue',
]

def get_file_design(ext):
    if (ext.lower() == 'docx'):
        return 'RoyalBlue'
    if (ext.lower() == 'xlsx'):
        return 'Green'
    if (ext.lower() == 'msg'):
        return 'Gold'
    if (ext.lower() == 'pdf'):
        return 'Brown'
    if (ext.lower() == 'xml'):
        return 'Teal'
    if (ext.lower() == 'xsd'):
        return 'SteelBlue'
    l = 0
    for c in ext:
        l += ord(c)
    return FILE_DESIGN[l % 26]

class File():
    
    def __init__(self, id, name, ext, size, url):
        self.id = id
        self.name = name
        self.ext = ext
        self.size = size
        self.url = url
        self.design = get_file_design(ext)

    def sizeof_fmt(self, suffix='b'):
        num = self.size
        for unit in ['','K','M','G','T','P','E','Z']:
            if abs(num) < 1024.0:
                if (unit == ''):
                    return "%3.0f %s%s" % (num, unit, suffix)
                else:
                    return "%3.1f %s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)

def get_attach_path(user, app, role, item_id):
    item = get_object_or_404(Task.objects.filter(user=user.id, id=item_id))
    ret = app + '/' + role + '_' + str(item_id)
    if (app == const.APP_APART):
        match (role, item.app_apart):
            case (const.ROLE_APART, const.NUM_ROLE_APART):
                ret = const.APP_APART + '/' + item.name
            case (const.ROLE_PRICE, const.NUM_ROLE_PRICE):
                ret = const.APP_APART + '/' + item.task_1.name + '/price/' + APART_SERVICE[item.price_service] + '/' + item.start.strftime('%Y.%m.%d')
            case (const.ROLE_METER, const.NUM_ROLE_METER):
                ret = const.APP_APART + '/' + item.task_1.name + '/meter/' + str(item.start.year) + '/' + str(item.start.month).zfill(2)
            case (const.ROLE_BILL, const.NUM_ROLE_BILL):
                ret = const.APP_APART + '/' + item.task_1.name + '/bill/' + str(item.start.year) + '/' + str(item.start.month).zfill(2)
    if (app == const.APP_FUEL):
        match (role, item.app_fuel):
            case (const.ROLE_CAR, const.NUM_ROLE_CAR):
                ret = const.APP_FUEL + '/' + item.name + '/car'
            case (const.ROLE_PART, const.NUM_ROLE_PART):
                ret = const.APP_FUEL + '/' + item.task_1.name + '/part/' + item.name
            case (const.ROLE_SERVICE, const.NUM_ROLE_SERVICE):
                ret = const.APP_FUEL + '/' + item.task_1.name + '/service/' + item.task_2.name + '/' + item.event.strftime('%Y.%m.%d')
            case (const.ROLE_FUEL, const.NUM_ROLE_FUEL):
                ret = const.APP_FUEL + '/' + item.task_1.name + '/fuel/' + item.event.strftime('%Y.%m.%d')
    return storage_path.format(user.username) + 'attachments/' + ret + '/'

def get_files_list_by_path(ret, path):
    fs = FileSystemStorage(location=path, base_url=file_storage_url)
    try:
        npp = 1
        for fname in fs.listdir('')[1]:
            name = os.path.splitext(fname)[0]
            ext = os.path.splitext(fname)[1][1:]
            size = os.path.getsize(path + fname)
            url = file_storage_url + fname
            fl = File(npp, name, ext, size, url)
            npp += 1
            ret.append(fl)
    except FileNotFoundError:
        pass

def get_files_list(user, app, role, item_id):
    ret = []
    fss_path = get_attach_path(user, app, role, item_id)
    get_files_list_by_path(ret, fss_path)
    return ret

def get_app_doc(app, role, request, pk, fname):
    path = get_attach_path(request.user, app, role, pk)
    try:
        fsock = open(path + fname, 'rb')
        return FileResponse(fsock)
    except IOError:
        return HttpResponseNotFound()


