import os, time, mimetypes, glob
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from task.const import *
from task.models import Task, detect_group
from rusel.base.config import Config
from rusel.base.forms import CreateGroupForm
from rusel.context import get_base_context
from rusel.utils import extract_get_params

class Context:
    def set_config(self, config, cur_view):
        self.config = Config(config, cur_view)

    def get_app_context(self, user_id, search_qty=None, icon=None, nav_items=None, **kwargs):
        context = {}
        if hasattr(self, 'object') and self.object:
            title = self.object.name
        else:
            if 'title' in kwargs:
                title = kwargs['title']
            else:
                title = _(self.config.title).capitalize()
        nav_item = None
        if (Task.get_nav_role(self.config.app) != self.config.get_cur_role()):
            nav_item = Task.get_active_nav_item(user_id, self.config.app)
            if nav_item:
                title = (title, nav_item.name)
                context['nav_item'] = nav_item
        context.update(get_base_context(self.request, self.config.app, self.config.get_cur_role(), self.config.cur_view_group, (hasattr(self, 'object') and self.object != None), title, icon=icon))
        context['fix_list'] = self.get_fixes(self.config.views, search_qty)
        context['group_form'] = CreateGroupForm()
        context['config'] = self.config
        context['params'] = extract_get_params(self.request, self.config.group_entity)
        if nav_items:
            context['nav_items'] = nav_items
        context['add_item_placeholder'] = '{} {}'.format(_('add').capitalize(), self.config.item_name if self.config.item_name else self.config.get_cur_role())
        if self.config.add_button:
            context['add_item_template'] = 'base/add_item_button.html'
        else:
            context['add_item_template'] = 'base/add_item_input.html'

        if (self.config.group_entity in self.request.GET):
            context['current_group'] = self.request.GET[self.config.group_entity]
        elif ('ret' in self.request.GET):
            context['current_group'] = self.request.GET['ret']

        return context

    def get_sorts(self, sorts):
        ret = []
        for sort in sorts:
            ret.append({'id': sort[0], 'name': _(sort[1]).capitalize()})
        return ret

    def get_fixes(self, views, search_qty):
        fixes = []
        if (self.config.app == APP_ALL):
            common_url = reverse('index')
        else:
            common_url = reverse(self.config.app + ':list')
        nav_item=Task.get_active_nav_item(self.request.user.id, self.config.app)
        for key, value in views.items():
            url = common_url
            determinator = 'view'
            view_id = self.config.main_view
            if (view_id != key):
                if ('role' in value):
                    determinator = 'role'
                    view_id = value['role']
                    url += view_id + '/'
                else:
                    view_id = key
                    if (key != self.config.main_view):
                        if ('page_url' in value):
                            url += value['page_url'] + '/'
                        else:
                            url += '?view=' + key
            hide_qty = False
            if ('hide_qty' in value):
                hide_qty = value['hide_qty']
            if hide_qty:
                qty = None
            else:
                if (view_id == self.config.group_entity):
                    _nav_item = None
                else:
                    _nav_item = nav_item
                fix_group = detect_group(self.request.user, self.config.app, determinator, view_id, _(value['title']).capitalize())
                qty = self.get_view_qty(fix_group, _nav_item)
            active = (self.config.cur_view_group.determinator == determinator) and (self.config.cur_view_group.view_id == view_id)
            fix = {
                'determinator': determinator,
                'id': view_id, 
                'url': url, 
                'icon': value['icon'], 
                'title': _(value['title']).capitalize(), 
                'qty': qty,
                'active': active,
                'search_qty': search_qty,
            }
            fixes.append(fix)
        return fixes

    def get_view_qty(self, group, nav_item):
        data = self.get_dataset(group, nav_item=nav_item)
        return len(data)    

    def get_dataset(self, group, query=None, nav_item=None):
        if (group.determinator == 'role'):
            cur_role = group.view_id
        else:
            cur_role = self.config.base_role
        data = Task.get_role_tasks(self.request.user.id, self.config.app, cur_role, nav_item)

        if (self.config.app == APP_ALL) and (not query):
            return data

        if data and ((not group.determinator) or (group.determinator == 'group')):
            data = data.filter(groups__id=group.id)
            # if (not group.completed):
            #     data = data.filter(completed=False)
        
        if hasattr(self, 'tune_dataset'):
            return self.tune_dataset(data, group)

        return data

    def get_nav_items(self):
        nav_role = Task.get_nav_role(self.config.app)
        if (not nav_role) or (nav_role == self.config.cur_view_group.view_id):
            return None
        href = self.request.path
        if ('pk' in self.kwargs):
            pk = str(self.kwargs['pk']) + '/'
            if (pk in href):
                href = href.split(pk)[0]
        sort = 'name'
        nav_item_group = detect_group(self.request.user, self.config.app, 'role', nav_role, '')
        if nav_item_group and nav_item_group.items_sort:
            sort = nav_item_group.items_sort
        ret = []
        for item in Task.get_role_tasks(self.request.user.id, self.config.app, nav_role).order_by(sort):
            ret.append({
                'id': item.id, 
                'name': item.name, 
                'qty': len(Task.get_role_tasks(self.request.user.id, self.config.app, self.config.cur_view_group.view_id, item)), 
                'href': href, 
                })
        return ret


class DirContext(Context):

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request)
        self.object = None
        self.cur_folder = ''
        page_title = ''
        title = ''
        if ('folder' in self.request.GET):
            self.cur_folder = self.request.GET['folder']
            page_title = self.cur_folder.split('/')[-1:][0]
            title = self.cur_folder
        if not self.cur_folder:
            page_title = _(self.config.app_title)
            title = page_title
        kwargs.update({'title': page_title})
        dir_tree = []
        self.scan_dir_tree(dir_tree, self.cur_folder, self.store_dir.rstrip('/'))
        self.scan_files()
        self.object = None
        context = super().get_context_data(**kwargs)
        upd_context = self.get_app_context(self.request.user.id, None, icon=self.config.view_icon, nav_items=None, **kwargs)
        context.update(upd_context)
        context['title'] = title
        context['dir_tree'] = dir_tree
        context['file_list'] = self.file_list
        context['gps_data'] = self.gps_data
        if (self.config.cur_view_group.determinator == 'view') and (self.config.cur_view_group.view_id != self.config.main_view):
            context['cur_view'] = self.config.cur_view_group.view_id
        context['theme_id'] = 24
        context['cur_folder'] = self.cur_folder
        return context

    def scan_dir_tree(self, dir_tree, cur_folder, path, parent=None, demo=False):
        ld = glob.glob(path + '/*/')
        if not len(ld):
            return
        node = ''
        level = 0
        if parent:
            node = parent['node']
            if node:
                node += '/'
            node += parent['name']
            level = parent['level'] + 1
        s_node = node
        if node:
            s_node = node + '/'
        p = path
        for d in ld:
            dd = d.replace('\\', '/')
            name = dd.split(p)[1].strip('/')
            x = {
                'node': node, 
                'name': name, 
                'active': (cur_folder == s_node + name), 
                'level': level, 
                'qty': 0,
                }
            dir_tree.append(x)
            if not demo:
                self.scan_dir_tree(dir_tree, cur_folder, path + '/' + name, x)

    def scan_files(self):
        self.gps_data = []
        self.file_list = []
        fd = glob.glob(self.store_dir + self.cur_folder + '/*')
        if not len(fd):
            return self.gps_data
        for f in fd:
            ff = f.replace('\\', '/')
            name = ff.split(self.store_dir + self.cur_folder)[1].strip('/')
            mt = mimetypes.guess_type(ff)
            file_type = ''
            if mt and mt[0]:
                file_type = mt[0]
            self.file_list.append({
                'name': name, 
                'date': time.ctime(os.path.getmtime(ff)),
                'type': file_type,
                'size': self.sizeof_fmt(os.path.getsize(ff)),
                })
        return self.gps_data

    def sizeof_fmt(self, num, suffix='B'):
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(num) < 1024.0:
                return f'{num:3.1f}{unit}{suffix}'
            num /= 1024.0
        return f'{num:.1f}Yi{suffix}'
