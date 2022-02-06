import os, time, mimetypes
from django.utils.translation import gettext_lazy as _
from task.const import ROLE_DOC, ROLE_APP
from task.models import Task
from rusel.base.views import BaseListView, BaseDetailView, BaseGroupView
from rusel.files import storage_path
from docs.forms import CreateForm, EditForm, FolderForm
from docs.config import app_config

role = ROLE_DOC
app = ROLE_APP[role]

class TuneData:
    def tune_dataset(self, data, group):
        return data

class ListView(BaseListView, TuneData):
    model = Task
    form_class = CreateForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)
        self.template_name = 'docs/folder.html'

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request)
        self.object = None
        context = super().get_context_data(**kwargs)
        cur_folder = ''
        if ('folder' in self.request.GET):
            cur_folder = self.request.GET['folder']
        dir_list = []
        file_list = []
        store_dir = storage_path.format(self.request.user.id) + 'docs/'
        for root, dirs, files in os.walk(store_dir):
            node = root.split(store_dir)[1].replace('\\', '/').lstrip('/')
            s_node = node
            if node:
                s_node = node + '/'
            node_level = 0
            node_item = None
            if node and (len(dirs) or len(files)):
                node_name = node.split('/')[-1:][0]
                for x in dir_list:
                    if (x['name'] == node_name):
                        node_level = x['level']
                        node_item = x
                        break
            for name in dirs:
                dir_list.append({
                    'node': node, 
                    'name': name, 
                    'active': (cur_folder == s_node + name), 
                    'level': node_level+1, 
                    'qty': 0,
                    })
            if node_item and len(files):
                node_item['qty'] = len(files)
            if (root.replace('\\', '/') == store_dir + cur_folder):
                for dir in dirs:
                    file_list.append({
                        'name': dir, 
                        'type': _('file folder').capitalize(), 
                        'date': time.ctime(os.path.getmtime(root + '/' + dir)),
                        })
                for name in files:
                    mt = mimetypes.guess_type(root + '/' + name)
                    file_type = ''
                    if mt and mt[0]:
                        file_type = mt[0]
                    file_list.append({
                        'name': name, 
                        'date': time.ctime(os.path.getmtime(root + '/' + name)),
                        'type': file_type,
                        'size': self.sizeof_fmt(os.path.getsize(root + '/' + name)),
                        })
        dir_tree = []
        self.dir_list_to_tree(dir_list, dir_tree, '')
        context['dir_tree'] = dir_tree
        context['file_list'] = file_list
        title = cur_folder
        if not title:
            title = _(self.config.app_title)
        context['title'] = title
        context['theme_id'] = 24
        return context

    def sizeof_fmt(self, num, suffix='B'):
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(num) < 1024.0:
                return f'{num:3.1f}{unit}{suffix}'
            num /= 1024.0
        return f'{num:.1f}Yi{suffix}'
    
    def dir_list_to_tree(self, dir_list, dir_tree, cur_node):
        for x in dir_list:
            if (x['node'] == cur_node):
                dir_tree.append(x)
                if cur_node:
                    node = cur_node + '/' + x['name']
                else:
                    node = x['name']
                self.dir_list_to_tree(dir_list, dir_tree, node)

class DetailView(BaseDetailView, TuneData):
    model = Task
    form_class = EditForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

class FolderView(BaseGroupView, TuneData):
    form_class = FolderForm

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

