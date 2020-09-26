import os
from django.core.files.storage import FileSystemStorage

file_storage_path = 'C:/Web/apps/docs/user_{}/'
file_storage_url = 'docs/'
    
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
]

def get_file_design(ext):
    l = 0
    for c in ext:
        l += ord(c)
    return FILE_DESIGN[l % 21]

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

def get_files_list(user, app_name, path):
    ret = []
    fss_path = file_storage_path.format(user.id) + app_name + '/' + path + '/'
    fs = FileSystemStorage(location = fss_path, base_url = file_storage_url)
    try:
        npp = 1
        for filename in fs.listdir('')[1]:
            name = os.path.splitext(filename)[0]
            ext = os.path.splitext(filename)[1][1:]
            size = os.path.getsize(fss_path + filename)
            url = file_storage_url + filename
            fl = File(npp, name, ext, size, url)
            npp += 1
            ret.append(fl)
    except FileNotFoundError:
        pass
    return ret
