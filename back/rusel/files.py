import os
from django.urls import reverse
from django.core.files.storage import FileSystemStorage

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

def get_file_design(ext, is_image):
    if (is_image):
        return 'LightGray'
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
    
    def __init__(self, role, task_id, id, name, ext, size):
        self.id = id
        self.name = name
        self.ext = ext
        self.size = size
        self.url = reverse('doc', args=(role, task_id, name + '.' + ext))
        self.tn_url = reverse('thumbnail', args=(role, task_id, name + '.' + ext))
        self.is_image = (self.ext in ('png', 'jpg', 'jpeg', 'bmp'))
        self.design = get_file_design(ext, self.is_image)

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

def get_files_list_by_path(role, task_id, path):
    fs = FileSystemStorage(location=path, base_url=file_storage_url)
    try:
        ret = []
        npp = 1
        for fname in fs.listdir('')[1]:
            name = os.path.splitext(fname)[0]
            ext = os.path.splitext(fname)[1][1:]
            size = os.path.getsize(path + fname)
            fl = File(role, task_id, npp, name, ext, size)
            npp += 1
            ret.append(fl)
        return ret
    except FileNotFoundError:
        return []

def get_files_list_by_path_v2(user, role, task_id, path):
    storage_path = os.environ.get('DJANGO_STORAGE_PATH', '')
    full_path = storage_path.format(user.username) + 'attachments/' + path + '/'
    fs = FileSystemStorage(location=full_path, base_url=file_storage_url)
    try:
        ret = []
        npp = 1
        for fname in fs.listdir('')[1]:
            name = os.path.splitext(fname)[0]
            ext = os.path.splitext(fname)[1][1:]
            size = os.path.getsize(full_path + fname)
            fl = File(role, task_id, npp, name, ext, size)
            npp += 1
            ret.append(fl)
        return ret
    except FileNotFoundError:
        return []
