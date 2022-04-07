from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from task.const import *
from task.models import Task, Group, detect_group

class Config:
    def __init__(self, config, cur_view_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cur_view_group = None
        self.app = config['name']
        self.app_title = _(config['app_title']).capitalize()
        self.title = config['app_title']
        self.app_icon = config['icon']
        self.view_icon = config['icon']
        self.role_icon = config['icon']
        self.views = config['views']
        self.base_role = self.check_property(config, 'role', None)
        self.main_view = self.check_property(config, 'main_view', None)
        if self.main_view:
            self.base_role = self.check_property(config['views'][self.main_view], 'role', self.base_role)
        self.use_groups = self.check_property(config, 'use_groups', False)
        self.group_entity = self.check_property(config, 'group_entity', 'group')
        self.use_selector = self.check_property(config, 'use_selector', False)
        self.use_important = self.check_property(config, 'use_important', False)
        self.add_button = self.check_property(config, 'add_button', False)
        self.item_name = self.check_property(config, 'item_name', '')
        self.event_in_name = self.check_property(config, 'event_in_name', False)
        self.use_sub_groups = False
        self.limit_list = 0
        self.app_sorts = None
        self.default_sort = '-event'
        if 'sort' in config and config['sort']:
            self.app_sorts = config['sort']
    
    def is_num(self, value):
        try:
            return (int(value) > 0)
        except:
            return False

    def set_view(self, request, detail=False):
        if not self.app:
            return
        self.cur_view_group = None
        self.nav_item = None
        determinator = 'view'
        view_id = ''
        if (self.app == APP_ALL):
            common_url = reverse('index')
            view_id = 'search'
        else:
            common_url = reverse(self.app + ':list')
        if self.main_view:
            view_id = self.main_view
        if (request.path != common_url):
            view_id = request.path.split(common_url)[1].split('?')[0].split('/')[0]
            if detail and self.is_num(view_id):
                view_id = request.path.split(common_url)[1].split('?')[0].split(view_id)[0]

            if view_id and (view_id in self.views):
                if ('page_url' in self.views[view_id]) and (self.views[view_id]['page_url'] == view_id):
                    determinator = 'view'
                else:
                    determinator = 'role'

        if (not view_id):
            view_id = self.main_view

        if ('view' in request.GET):
            view_name = request.GET.get('view')
            if view_name:
                view_id = view_name
        nav_role = Task.get_nav_role(self.app)
        if (not nav_role) and (self.group_entity in request.GET):
            group_id = request.GET.get(self.group_entity)
            if group_id and int(group_id) and Group.objects.filter(user=request.user.id, id=int(group_id)).exists():
                determinator = 'group'
                view_id = group_id
                self.title = Group.objects.filter(user=request.user.id, id=int(group_id)).get().name
                self.role_icon = self.app_icon
                self.view_icon = self.app_icon
        self.view_sorts = None
        if (determinator != 'group') and (view_id in self.views):
            if (determinator == 'role')  and ('role' in self.views[view_id]):
                self.role_icon = self.check_property(self.views[view_id], 'icon', self.role_icon)
                self.view_icon = self.check_property(self.views[view_id], 'icon', self.view_icon)
            else:
                self.role_icon = self.app_icon
            if (determinator == 'view'):
                self.view_icon = self.check_property(self.views[view_id], 'icon', self.view_icon)
            self.title = self.check_property(self.views[view_id], 'title', self.title)
            self.use_selector = self.check_property(self.views[view_id], 'use_selector', self.use_selector)
            self.use_important = self.check_property(self.views[view_id], 'use_important', self.use_important)
            self.add_button = self.check_property(self.views[view_id], 'add_button', self.add_button)
            self.item_name = self.check_property(self.views[view_id], 'item_name', self.item_name)
            self.event_in_name = self.check_property(self.views[view_id], 'event_in_name', self.event_in_name)
            self.use_sub_groups = self.check_property(self.views[view_id], 'use_sub_groups', self.use_sub_groups)
            self.limit_list = self.check_property(self.views[view_id], 'limit_list', self.limit_list)
            if 'sort' in self.views[view_id]:
                self.view_sorts = self.views[view_id]['sort']

        if (determinator == 'group'):
            self.use_sub_groups = (self.app in (APP_TODO, APP_STORE))

        if determinator and view_id:
            self.cur_view_group = detect_group(request.user, self.app, determinator, view_id, _(self.title).capitalize())

    def check_property(self, config, prop, default):
        ret = default
        if (prop in config):
            ret = config[prop]
        return ret

    def get_cur_role(self):
        if (self.cur_view_group and self.cur_view_group.determinator and self.cur_view_group.determinator == 'role'):
            return self.cur_view_group.view_id
        return self.base_role

