import os, glob, mimetypes
from django.urls import reverse
from task.const import *
from task.models import Task
from rusel.files import storage_path

class SearchResult:
    def __init__(self, query, role, folder, file, is_folder=False, photo_num=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query = query
        self.role = role
        self.folder = folder
        self.file = file
        self.hide_params = True
        self.is_folder = is_folder
        self.photo_num = photo_num

    def get_roles(self):
        return [{'icon': ROLE_ICON[self.role], 'href': self.get_absolute_url(), 'name': self.role, 'hide_params': True}]

    def get_absolute_url(self):
        if (self.role == ROLE_PHOTO):
            if self.is_folder:
                return reverse('photo:list') + '?folder=' + self.folder
            return reverse('photo:detail') + '?folder=' + self.folder + '#photo-' + str(self.photo_num)
        if (self.role == ROLE_WARR):
            if Task.objects.filter(app_warr=NUM_ROLE_WARR, name=self.folder).exists():
                task = Task.objects.filter(app_warr=NUM_ROLE_WARR, name=self.folder).get()
                return reverse('warr:item', args=(task.id,))
        return reverse('docs:list') + '?folder=' + self.folder

    def name(self):
        return self.highlight_search(self.file)

    def get_item_attr(self):
        ret = {self.role: {'attr': [], 'group': self.highlight_search(self.folder.replace('\\', '/'))}}
        if self.is_folder:
            ret[self.role]['attr'].append({'icon': 'folder'})
        return ret

    def highlight_search(self, value):
        strong = '<strong>' + self.query + '</strong>'
        if self.query in value:
            value = strong.join(value.split(self.query))
        return value

def search_in_files(user, app, start_folder, query):
    ret = []

    docs_dir = None
    if not app or app == APP_DOCS:
        docs_dir = storage_path.format(user.username) + 'docs'
        if start_folder:
            docs_dir += '/' + start_folder

    photo_dir = None
    if not app or app == APP_PHOTO:
        photo_dir = storage_path.format(user.username) + 'photo'
        if start_folder:
            photo_dir += '/' + start_folder

    warr_dir = None
    if not app or app == APP_WARR:
        warr_dir = storage_path.format(user.username) + 'attachments\\warr'
        if start_folder:
            warr_dir += '/' + start_folder

    process_dir(ret, query, ROLE_DOC, docs_dir, start_folder)
    process_dir(ret, query, ROLE_PHOTO, photo_dir, start_folder)
    process_dir(ret, query, ROLE_WARR, warr_dir, start_folder)
    return ret

def process_dir(ret, query, role, store_dir, start_folder):
    if not store_dir:
        return

    for item in glob.glob('**\\*' + query + '*', root_dir=store_dir, recursive=True):
        folder = ''
        search_folder = ''
        if start_folder:
            folder = start_folder
        file = item
        is_folder = os.path.isdir(store_dir.replace('/', '\\') + '\\' + item)
        sep = item.rfind('\\')
        if (sep > 0):
            if folder:
                folder += '/'
            search_folder = item[:sep].replace('\\', '/')
            folder += search_folder
            file = item[sep+1:]
        num = None
        if is_folder:
            folder += '/' + file
        elif role == ROLE_PHOTO:
            if not is_image(store_dir.replace('/', '\\') + '\\' + item):
                continue
            num = get_photo_num(store_dir, search_folder, file)
        ret.append(SearchResult(query, role, folder, file, is_folder=is_folder, photo_num=num))


def get_photo_num(store_dir, folder, file):
    num = 0
    with os.scandir(store_dir + '/' + folder) as it:
        for entry in it:
            if (entry.name.upper() == 'Thumbs.db'.upper()):
                continue
            if entry.is_dir():
                continue
            if not is_image(entry.path):
                continue
            if (file == entry.name):
                return num
            num += 1
    return 0

def is_image(path):
    mt = mimetypes.guess_type(path)
    file_type = '???'
    if mt and mt[0]:
        file_type = mt[0]
    if '/' in file_type and (file_type.split('/')[0] == 'image' or file_type.split('/')[0] == 'video'):
        return True
    return False
