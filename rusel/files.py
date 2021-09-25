import os
from django.core.files.storage import FileSystemStorage
from rusel.secret import storage_dvlp, storage_prod, service_dvlp, service_prod, folder_dvlp, folder_prod

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

def get_files_list(user, app, role, item_id):
    ret = []
    fss_path = storage_path.format(user.id) + app + '/' + role + '_' + str(item_id) + '/'
    fs = FileSystemStorage(location = fss_path, base_url = file_storage_url)
    try:
        npp = 1
        for fname in fs.listdir('')[1]:
            name = os.path.splitext(fname)[0]
            ext = os.path.splitext(fname)[1][1:]
            size = os.path.getsize(fss_path + fname)
            url = file_storage_url + fname
            fl = File(npp, name, ext, size, url)
            npp += 1
            ret.append(fl)
    except FileNotFoundError:
        pass
    return ret
