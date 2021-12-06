import os, json
from datetime import date
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.http import FileResponse, HttpResponseNotFound
from django.views.generic.edit import CreateView, UpdateView
from django.db.models import Q
from django.core.exceptions import FieldError
from rusel.apps import get_related_roles
from rusel.context import get_base_context
from rusel.files import storage_path, get_files_list
from rusel.utils import extract_get_params, get_search_mode
from rusel.base.forms import GroupForm, CreateGroupForm
from task.const import *
from task.models import Task, Group, TaskGroup, Urls

class Config:
    def __init__(self, config, cur_view_name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = config['name']
        self.app_title = _(config['app_title']).capitalize()
        self.title = config['app_title']
        self.icon = config['icon']
        self.views = config['views']
        self.base_role = config['role']
        self.use_groups = self.check_property(config, 'use_groups', False)
        self.use_selector = self.check_property(config, 'use_selector', False)
        self.use_important = self.check_property(config, 'use_important', False)
        self.add_button = self.check_property(config, 'add_button', False)
        self.item_name = self.check_property(config, 'item_name', '')
        self.multy_role = False
        for key, value in self.views.items():
            if ('role' in value):
                self.multy_role = True
                break;
        self.cur_view_group = None

    def set_view(self, request):
        self.cur_view_group = None
        common_url = reverse(self.app + ':list')
        determinator = 'role'
        view_id = self.base_role
        if (self.multy_role):
            if (request.path != common_url):
                role_name = request.path.split(common_url)[1].split('?')[0].split('/')[0]
                determinator = 'role'
                view_id = role_name
        if ('view' in request.GET):
            view_name = request.GET.get('view')
            determinator = 'view'
            view_id = view_name
        if ('group' in request.GET):
            group_id = int(request.GET.get('group'))
            if Group.objects.filter(id=group_id).exists():
                determinator = 'group'
                view_id = str(group_id)
                self.title = Group.objects.filter(id=group_id).get().name
        if (determinator != 'group') and (view_id in self.views):
            self.title = self.check_property(self.views[view_id], 'title', self.title)
            self.icon = self.check_property(self.views[view_id], 'icon', self.icon)
            self.use_selector = self.check_property(self.views[view_id], 'use_selector', self.use_selector)
            self.use_important = self.check_property(self.views[view_id], 'use_important', self.use_important)
            self.add_button = self.check_property(self.views[view_id], 'add_button', self.add_button)
            self.item_name = self.check_property(self.views[view_id], 'item_name', self.item_name)
        if determinator and view_id:
            self.cur_view_group = detect_group(request.user, self.app, determinator, view_id, self.title)

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

    def get_app_context(self, **kwargs):
        context = {}
        title = _(self.config.title).capitalize()
        context.update(get_base_context(self.request, self.config.app, self.config.get_cur_role(), False, title))
        context['fix_list'] = self.get_fixes(self.config.views)
        context['group_form'] = CreateGroupForm()
        #context['sort_options'] = self.get_sorts()
        role = self.config.get_cur_role()
        if (role == self.config.base_role):
            context['item_detail_url'] = self.config.app + ':item'
        else:
            context['item_detail_url'] = self.config.app + ':' + role + '-item'
        context['config'] = self.config
        context['params'] = extract_get_params(self.request)
        return context

    def get_fixes(self, views):
        fixes = []
        common_url = reverse(self.config.app + ':list')
        for key, value in views.items():
            url = common_url
            determinator = 'role'
            view_id = self.config.base_role
            if (view_id != key):
                if ('role' in value):
                    view_id = value['role']
                    url += view_id + '/'
                else:
                    view_id = key
                    determinator = 'view'
                    url += '?view=' + key
            qty = self.get_view_qty(detect_group(self.request.user, self.config.app, determinator, view_id, self.config.title))
            fix = {
                'determinator': determinator,
                'id': view_id, 
                'url': url, 
                'icon': value['icon'], 
                'title': _(value['title']).capitalize(), 
                'qty': qty,
                'active': (self.config.cur_view_group.determinator == determinator) and (self.config.cur_view_group.view_id == view_id)
            }
            fixes.append(fix)
        return fixes

    def get_view_qty(self, group):
        data = self.get_dataset(group)
        return len(data)    

    def get_dataset(self, group):
        data = Task.objects.filter(user=self.request.user.id)

        if (group.determinator == 'role'):
            cur_role = group.view_id
        else:
            cur_role = self.config.base_role
        role_id = ROLES_IDS[self.config.app][cur_role]

        if (self.config.app == APP_TODO):
            data = data.filter(app_task=role_id)
        if (self.config.app == APP_NOTE):
            data = data.filter(app_note=role_id)
        if (self.config.app == APP_NEWS):
            data = data.filter(app_news=role_id)
        if (self.config.app == APP_STORE):
            data = data.filter(app_store=role_id)
        if (self.config.app == APP_DOCS):
            data = data.filter(app_doc=role_id)
        if (self.config.app == APP_WARR):
            data = data.filter(app_warr=role_id)
        if (self.config.app == APP_EXPEN):
            data = data.filter(app_expen=role_id)
        if (self.config.app == APP_TRIP):
            data = data.filter(app_trip=role_id)
        if (self.config.app == APP_FUEL):
            data = data.filter(app_fuel=role_id)
        if (self.config.app == APP_APART):
            data = data.filter(app_apart=role_id)
        if (self.config.app == APP_HEALTH):
            data = data.filter(app_health=role_id)
        if (self.config.app == APP_WORK):
            data = data.filter(app_work=role_id)
        if (self.config.app == APP_PHOTO):
            data = data.filter(app_photo=role_id)

        if data and ((not group.determinator) or (group.determinator == 'group')):
            data = data.filter(groups__id=group.id)
            if (not group.completed):
                data = data.filter(completed=False)
        
        return self.tune_dataset(data, group)

class BaseListView(CreateView, Context):

    def __init__(self, config, cur_role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(config, cur_role)
        self.template_name = 'base/list.html'

    def get_queryset(self):
        self.config.set_view(self.request)
        return self.get_dataset(self.config.cur_view_group)

    def get_success_url(self):
        if (self.config.get_cur_role() == self.config.base_role):
            return reverse(self.config.app + ':item', args=(self.object.id,)) + extract_get_params(self.request)
        return reverse(self.config.app + ':' + self.config.get_cur_role() + '-item', args=(self.object.id,)) + extract_get_params(self.request)

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context())
        context['add_item_placeholder'] = '{} {}'.format(_('add').capitalize(), self.config.item_name if self.config.item_name else self.config.get_cur_role())
        context['add_button'] = self.config.add_button

        sub_groups = self.load_sub_groups()
        query = None
        if (self.request.method == 'GET'):
            query = self.request.GET.get('q')
        #search_mode = 0

        tasks = self.get_sorted_items(query)
        for task in tasks:
            grp_id = self.get_sub_group_id(task.stop, task.completed)
            group = self.find_sub_group(sub_groups, grp_id, GRPS_PLANNED[grp_id].capitalize())
            group['items'].append(task)

        self.save_sub_groups(sub_groups)
        
        context['sub_groups'] = sorted(sub_groups, key = lambda group: group['id'])
        if self.config.cur_view_group and self.config.cur_view_group.theme:
            context['theme_id'] = self.config.cur_view_group.theme
        return context

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

    def get_sub_group_id(self, termin, completed):
        if completed and self.config.cur_view_group:
            return GRP_PLANNED_DONE
        if (not termin) or not ((self.config.cur_view_group.determinator == 'view' and self.config.cur_view_group.view_id == 'planned')):
            return GRP_PLANNED_NONE
        today = date.today()
        if (termin == today):
            return GRP_PLANNED_TODAY
        days = (termin.date() - today).days
        if (days == 1):
            return GRP_PLANNED_TOMORROW
        if (days < 0):
            return GRP_PLANNED_EARLIER
        if (days < 8):
            return GRP_PLANNED_ON_WEEK
        return GRP_PLANNED_LATER

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
        sort_mode = 'name' # todo
        sort_reverse = False # todo
        return self.sort_data(data, sort_mode + ' stop', sort_reverse)

    def get_filtered_items(self, query):
        ret = self.get_queryset()
        search_mode = get_search_mode(query)
        lookups = None
        if (search_mode == 0):
            return ret
        elif (search_mode == 1):
            lookups = Q(name__icontains=query) | Q(info__icontains=query)
        elif (search_mode == 2):
            lookups = Q(categories__icontains=query[1:])
        return ret.filter(lookups)

    def sort_data(self, data, sort, reverse):
        if not data:
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
            return reverse(self.config.app + ':item', args=(self.object.id,)) + extract_get_params(self.request)
        return reverse(self.config.app + ':' + self.config.get_cur_role() + '-item', args=(self.object.id,)) + extract_get_params(self.request)

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context())
        context['title'] = self.object.name
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
        return reverse(self.config.app + ':group', args=(self.object.id,)) + extract_get_params(self.request)

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context())
        context['title'] = self.object.name
        context['delete_question'] = _('delete group').capitalize()
        if Group.objects.filter(node=self.object.id).exists():
            context['ban_on_deletion'] = _('deletion is prohibited because there are subordinate groups').capitalize()
        else:
            if TaskGroup.objects.filter(group=self.object.id).exists():
                context['ban_on_deletion'] = _('deletion is prohibited because the group contains items').capitalize()
            else:
                context['ban_on_deletion'] = ''
        return context

def get_app_doc(app, role, request, pk, fname):
    path = storage_path.format(request.user.id) + app + '/' + role + '_{}/'.format(pk)
    try:
        fsock = open(path + fname, 'rb')
        return FileResponse(fsock)
    except IOError:
        return HttpResponseNotFound()

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
