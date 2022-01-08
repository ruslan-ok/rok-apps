import os, json
from datetime import date
from django.http.response import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.db.models import Q
from django.core.exceptions import FieldError
from rusel.apps import get_related_roles
from rusel.context import get_base_context
from rusel.files import storage_path, get_files_list
from rusel.utils import extract_get_params, get_search_mode
from rusel.base.forms import GroupForm, CreateGroupForm
from task.const import *
from task.models import Task, Group, TaskGroup, Urls
from apart.forms.price import APART_SERVICE

BG_IMAGES = [
    'beach',
    'desert',
    'fern',
    'field',
    'gradient',
    'lighthouse',
    'safari',
    'sea',
    'tv_tower'
]

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

def detect_group(user, app, determinator, view_id, name):
    group = None
    if (determinator == 'group'):
        if Group.objects.filter(user=user.id, app=app, id=int(view_id)).exists():
            group = Group.objects.filter(user=user.id, app=app, id=int(view_id)).get()
    if (determinator == 'role'):
        if Group.objects.filter(user=user.id, app=app, determinator='role', view_id=view_id).exists():
            group = Group.objects.filter(user=user.id, app=app, determinator='role', view_id=view_id).get()
    if (determinator == 'view'):
        if Group.objects.filter(user=user.id, app=app, determinator='view', view_id=view_id).exists():
            group = Group.objects.filter(user=user.id, app=app, determinator='view', view_id=view_id).get()
    if not group and (determinator != 'group'):
        group = Group.objects.create(
            user=user, 
            app=app, 
            determinator=determinator, 
            view_id=view_id,
            name=name)
    return group

class Context:
    def set_config(self, config, cur_view):
        self.config = Config(config, cur_view)

    def get_app_context(self, user_id, search_qty=None, icon=None, nav_items=None, **kwargs):
        context = {}
        if self.object:
            title = self.object.name
        else:
            title = _(self.config.title).capitalize()
        nav_item = None
        if (Task.get_nav_role(self.config.app) != self.config.get_cur_role()):
            nav_item = Task.get_active_nav_item(user_id, self.config.app)
            if nav_item:
                title = (title, nav_item.name)
                context['nav_item'] = nav_item
        context.update(get_base_context(self.request, self.config.app, self.config.get_cur_role(), self.config.cur_view_group, (self.object != None), title, icon=icon))
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
            if (not group.completed):
                data = data.filter(completed=False)
        
        return self.tune_dataset(data, group)

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

class BaseListView(ListView, Context):

    def __init__(self, config, cur_role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(config, cur_role)
        self.template_name = 'base/list.html'

    def get(self, request, *args, **kwargs):
        ret = super().get(request, *args, **kwargs)
        nav_role = Task.get_nav_role(self.config.app)
        if nav_role and (nav_role != self.config.get_cur_role()):
            if (self.config.group_entity in request.GET):
                active_nav_item_id = request.GET[self.config.group_entity]
                Task.set_active_nav_item(request.user.id, self.config.app, active_nav_item_id)
            else:
                ani = Task.get_active_nav_item(request.user.id, self.config.app)
                if ani:
                    return HttpResponseRedirect(request.path + '?' + self.config.group_entity + '=' + str(ani.id))
        return ret

    def get_queryset(self):
        query = None
        if (self.request.method == 'GET'):
            query = self.request.GET.get('q')
        data = self.get_sorted_items(query)
        if self.config.limit_list:
            data = data[:self.config.limit_list]
        if query:
            for task in data:
                task = self.highlight_search(query, task)
        return data

    def highlight_search(self, query, task):
        strong = '<strong>' + query + '</strong>'
        if query in task.name:
            task.name = strong.join(task.name.split(query))
        if query in task.info:
            if (len(task.info) < 200):
                fnd_info = task.info
            else:
                prefix = ''
                pos = task.info.find(query)
                if (pos > 80):
                    pos -= 80
                    prefix = '... '
                else:
                    pos = 0
                fnd_info = prefix + task.info[pos:pos+200] + ' ...'
            task.found = strong.join(fnd_info.split(query))
        return task

    def get_success_url(self):
        if (self.config.get_cur_role() == self.config.base_role):
            return reverse(self.config.app + ':item', args=(self.object.id,)) + extract_get_params(self.request, self.config.group_entity)
        return reverse(self.config.app + ':' + self.config.get_cur_role() + '-item', args=(self.object.id,)) + extract_get_params(self.request, self.config.group_entity)

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request)
        self.object = None
        context = super().get_context_data(**kwargs)
        use_sub_groups = self.config.use_sub_groups and self.config.cur_view_group.use_sub_groups
        context['use_sub_groups'] = use_sub_groups
        if use_sub_groups:
            sub_groups = self.load_sub_groups()
            for task in self.get_queryset():
                grp_id, name = self.get_sub_group(task)
                group = self.find_sub_group(sub_groups, grp_id, name)
                group['items'].append(task)
            self.save_sub_groups(sub_groups)
            context['sub_groups'] = sorted(sub_groups, key = lambda group: group['id'])

        search_qty = None
        query = None
        if (self.request.method == 'GET'):
            query = self.request.GET.get('q')
        if query:
            search_qty = len(self.object_list)
        context.update(self.get_app_context(self.request.user.id, search_qty, icon=self.config.view_icon, nav_items=self.get_nav_items()))

        if self.config.view_sorts:
            context['sorts'] = self.get_sorts(self.config.view_sorts)
        elif self.config.app_sorts:
            context['sorts'] = self.get_sorts(self.config.app_sorts)

        themes = []
        for x in range(23):
            if (x < 14):
                themes.append({'id': x+1, 'style': 'theme-' + str(x+1)})
            else:
                themes.append({'id': x+1, 'img': self.get_bg_img(x)})
        context['themes'] = themes

        if self.config.cur_view_group and self.config.cur_view_group.theme:
            context['theme_id'] = self.config.cur_view_group.theme

        if self.config.cur_view_group.items_sort:
            context['sort_id'] = self.config.cur_view_group.items_sort
            context['sort_reverse'] = self.config.cur_view_group.items_sort[0] == '-'
            if self.config.view_sorts:
                sorts = self.config.view_sorts
            else:
                sorts = self.config.app_sorts
            for sort in sorts:
                if (sort[0] == self.config.cur_view_group.items_sort.replace('-', '')):
                    context['sort_name'] = _(sort[1]).capitalize()
                    break

        return context

    def get_bg_img(self, num):
        return BG_IMAGES[num-14]

    def load_sub_groups(self):
        cur_group = self.config.cur_view_group
        ret = []
        if not cur_group:
            return ret
        if not cur_group.sub_groups:
            return ret
        sgs = json.loads(cur_group.sub_groups)
        for sg in sgs:
            ret.append({'id': sg['id'], 'name': sg['name'], 'is_open': sg['is_open'], 'items': [], 'qty': 0 })
        return ret

    def save_sub_groups(self, sub_groups):
        cur_group = self.config.cur_view_group
        if not cur_group:
            return
        sub_groups_json = []
        for sg in sub_groups:
            if sg['id']:
                sub_groups_json.append({'id': sg['id'], 'name': sg['name'], 'is_open': sg['is_open']})
        sub_groups_str = json.dumps(sub_groups_json)
        cur_group.sub_groups = sub_groups_str
        cur_group.save()

    def get_sub_group(self, task):
        use_sub_groups = self.config.use_sub_groups and self.config.cur_view_group.use_sub_groups
        if not use_sub_groups:
            return 0, ''
        if (task.app_apart == NUM_ROLE_PRICE):
            return task.price_service, APART_SERVICE[task.price_service]
        if (task.app_fuel == NUM_ROLE_SERVICE):
            if not task.task_2:
                return 0, ''
            else:
                return task.task_2.id, task.task_2.name
        if task.completed and self.config.cur_view_group:
            grp_id = GRP_PLANNED_DONE
        elif (not task.stop) or not ((self.config.cur_view_group.determinator == 'view' and self.config.cur_view_group.view_id == 'planned')):
            grp_id = GRP_PLANNED_NONE
        else:
            today = date.today()
            if (task.stop == today):
                grp_id = GRP_PLANNED_TODAY
            else:
                days = (task.stop.date() - today).days
                if (days == 1):
                    grp_id = GRP_PLANNED_TOMORROW
                elif (days < 0):
                    grp_id = GRP_PLANNED_EARLIER
                elif (days < 8):
                    grp_id = GRP_PLANNED_ON_WEEK
                else:
                    grp_id = GRP_PLANNED_LATER
        return grp_id, GRPS_PLANNED[grp_id].capitalize()

    def find_sub_group(self, groups, grp_id, name):
        for group in groups:
            if (group['id'] == grp_id):
                group['qty'] += 1
                return group
        group = {'id': grp_id, 'name': name, 'is_open': True, 'items': [], 'qty': 1 }
        groups.append(group)
        return group

    def get_sorted_items(self, query):
        data = self.get_filtered_items(query)
        if not self.config.cur_view_group.items_sort:
            if self.config.default_sort:
                return self.sort_data(data, self.config.default_sort)
            return data
        return self.sort_data(data, self.config.cur_view_group.items_sort)

    def get_base_dataset(self):
        nav_role = Task.get_nav_role(self.config.app)
        if nav_role and (nav_role != self.config.get_cur_role()):
            if (self.config.group_entity in self.request.GET):
                active_nav_item_id = self.request.GET[self.config.group_entity]
                Task.set_active_nav_item(self.request.user.id, self.config.app, active_nav_item_id)
        self.config.set_view(self.request)
        query = None
        if (self.request.method == 'GET'):
            query = self.request.GET.get('q')
        nav_item = None
        if nav_role and (nav_role != self.config.get_cur_role()):
            nav_item = Task.get_active_nav_item(self.request.user.id, self.config.app)
        return self.get_dataset(self.config.cur_view_group, query, nav_item)

    def get_filtered_items(self, query):
        ret = self.get_base_dataset()
        search_mode = get_search_mode(query)
        lookups = None
        if (search_mode == 0):
            return ret
        elif (search_mode == 1):
            lookups = Q(name__icontains=query) | Q(info__icontains=query) | Q(categories__icontains=query)
        elif (search_mode == 2):
            lookups = Q(categories__icontains=query[1:])
        return ret.filter(lookups)

    def sort_data(self, data, sort, reverse=False):
        if not data or not sort:
            return data

        sort_fields = sort.split()
        if reverse:
            revers_list = []
            for sf in sort_fields:
                if (sf[0] == '-'):
                    revers_list.append(sf[1:])
                else:
                    revers_list.append('-' + sf)
            sort_fields = revers_list

        try:
            if (len(sort_fields) == 1):
                data = data.order_by(sort_fields[0])
            elif (len(sort_fields) == 2):
                data = data.order_by(sort_fields[0], sort_fields[1])
            elif (len(sort_fields) == 3):
                data = data.order_by(sort_fields[0], sort_fields[1], sort_fields[2])
        except FieldError:
            pass

        return data

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        self.config.set_view(self.request)
        if (self.config.cur_view_group):
            TaskGroup.objects.create(task=self.object, group=self.config.cur_view_group, role=self.config.app)
        return response
    
class BaseDetailView(UpdateView, Context):

    def __init__(self, config, cur_role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(config, cur_role)
        self.template_name = config['name'] + '/' + self.config.get_cur_role() + '.html'

    def get_success_url(self):
        if (self.config.get_cur_role() == self.config.base_role):
            return reverse(self.config.app + ':item', args=(self.object.id,)) + extract_get_params(self.request, self.config.group_entity)
        return reverse(self.config.app + ':' + self.config.get_cur_role() + '-item', args=(self.object.id,)) + extract_get_params(self.request, self.config.group_entity)

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request, detail=True)
        self.template_name = self.config.app + '/' + self.config.get_cur_role() + '.html'
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context(self.request.user.id, None, icon=self.config.role_icon, nav_items=self.get_nav_items()))
        urls = []
        for url in Urls.objects.filter(task=self.object.id):
            if (self.request.path not in url.href):
                urls.append(url)
            else:
                fake_url = url
                fake_url.href = '#'
                urls.append(fake_url)
        context['urls'] = urls
        context['files'] = get_files_list(self.request.user, self.config.app, self.config.get_cur_role(), self.object.id)
        context['item'] = self.object
        related_roles, possible_related = get_related_roles(self.get_object(), self.config)
        context['related_roles'] = related_roles
        context['possible_related'] = possible_related
        return context

    def form_valid(self, form):
        self.config.set_view(self.request, detail=True)
        item = form.instance
        if ('url' in form.changed_data):
            url = form.cleaned_data['url']
            qty = len(Urls.objects.filter(task=item.id))
            Urls.objects.create(task=item, num=qty, href=url)
        if ('upload' in self.request.FILES):
            self.handle_uploaded_file(self.request.FILES['upload'], self.request.user, item.id)
        ret = super().form_valid(form)
        if ('grp' in form.changed_data):
            grp = form.cleaned_data['grp']
            role = self.config.get_cur_role()
            if not grp and TaskGroup.objects.filter(task=item.id, role=role).exists():
                TaskGroup.objects.filter(task=item.id, role=role).delete()
            if grp:
                if not TaskGroup.objects.filter(task=item.id, role=role).exists():
                    TaskGroup.objects.create(task=item, group=grp, role=grp.role)
                else:
                    tg = TaskGroup.objects.filter(task=item.id, role=role).get()
                    if (tg.group != grp):
                        tg.group = grp
                        tg.save()
        return ret

    def handle_uploaded_file(self, f, user, item_id):
        path = storage_path.format(user.id) + self.config.app + '/' + self.config.get_cur_role() + '_{}/'.format(item_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path + f.name, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

class BaseGroupView(UpdateView, Context):
    model = Group
    template_name = 'base/group_detail.html'
    form_class = GroupForm

    def __init__(self, config, cur_role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(config, cur_role)

    def get_success_url(self):
        return reverse(self.config.app + ':group', args=(self.object.id,)) + extract_get_params(self.request, self.config.group_entity)

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request, detail=True)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context(self.request.user.id, None, icon='journals'))
        context['title'] = self.object.name
        context['is_group_form'] = self.object.name
        context['delete_question'] = _('delete group').capitalize()
        if Group.objects.filter(node=self.object.id).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because there are subordinate groups').capitalize()
        else:
            if TaskGroup.objects.filter(group=self.object.id).exists():
                context['ban_on_deletion'] = _('deletion is prohibited because the group contains items').capitalize()
            else:
                context['ban_on_deletion'] = ''
        return context


GRP_PLANNED_NONE     = 0
GRP_PLANNED_EARLIER  = 1
GRP_PLANNED_TODAY    = 2
GRP_PLANNED_TOMORROW = 3
GRP_PLANNED_ON_WEEK  = 4
GRP_PLANNED_LATER    = 5
GRP_PLANNED_DONE     = 6

GRPS_PLANNED = {
    GRP_PLANNED_NONE:     '',
    GRP_PLANNED_EARLIER:  _('earlier'),
    GRP_PLANNED_TODAY:    _('today'),
    GRP_PLANNED_TOMORROW: _('tomorrow'),
    GRP_PLANNED_ON_WEEK:  _('on the week'),
    GRP_PLANNED_LATER:    _('later'),
    GRP_PLANNED_DONE:     _('completed'),
}  
