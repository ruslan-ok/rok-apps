from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from rusel.context import get_base_context
from rusel.apps import get_app_by_role
from task.forms import GroupForm, CreateGroupForm
from task.const import ROLES_IDS
from task.models import Task, Group, TaskGroup

class Config:
    def __init__(self, config, cur_role, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = config['name']
        self.app_title = _(config['app_title']).capitalize()
        self.title = config['app_title']
        self.icon = config['icon']
        self.views = config['views']
        self.role = config['role']
        self.groups = self.check_property(config, 'groups', False)
        self.use_selector = self.check_property(config, 'use_selector', False)
        self.use_important = self.check_property(config, 'use_important', False)

        if (cur_role in self.views):
            self.cur_view = cur_role
            self.title = self.check_property(self.views[cur_role], 'title', self.title)
            self.icon = self.check_property(self.views[cur_role], 'icon', self.icon)

    def set_view(self, request):
        self.group_id = 0
        view_mode = ''
        if request.method == 'GET':
            if ('view' in request.GET):
                view_mode = request.GET.get('view')
            if (view_mode == 'by_group') and ('group_id' in request.GET):
                self.group_id = int(request.GET.get('group_id'))
        if view_mode and (view_mode in self.views):
            self.cur_view = view_mode
            self.title = self.check_property(self.views[view_mode], 'title', self.title)
            self.icon = self.check_property(self.views[view_mode], 'icon', self.icon)
        elif (view_mode == 'by_group') :           
            self.cur_view = view_mode

    def check_property(self, config, prop, default):
        ret = default
        if (prop in config):
            ret = config[prop]
        return ret

class Context:
    def set_config(self, config, cur_role):
        self.config = Config(config, cur_role)

    def get_app_context(self, **kwargs):
        context = {}
        title = _(self.config.title).capitalize()
        context.update(get_base_context(self.request, self.config.role, False, title))
        context['fix_list'] = self.get_fixes(self.config.views)
        context['group_form'] = CreateGroupForm()
        #context['sort_options'] = self.get_sorts()
        context['item_detail_url'] = self.config.app + ':item'
        context['config'] = self.config

        tasks = self.get_queryset()
        items = []
        for t in tasks:
            item = {
                'id': t.id,
                'name': t.name,
                'important': t.important,
                'completed': t.completed,
                'attrs': self.get_info(t)
            }
            items.append(item)
        context['items'] = items
        return context

    def get_fixes(self, views):
        fixes = []
        common_url = reverse(self.config.app + ':list')
        for key, value in views.items():
            url = common_url
            view_role = self.config.role
            if (self.config.role != key):
                if ('role' in value):
                    view_role = value['role']
                    url += view_role + '/'
            if (key != view_role):
                url += '?view=' + key
            qty = self.get_qty(key, 0)
            fixes.append({'name': key, 'url': url, 'icon': value['icon'], 'title': _(value['title']).capitalize(), 'qty': qty})
        return fixes

    def get_info(self, item):
        return []

    def get_qty(self, view_mode, group_id):
        data = self.get_dataset(view_mode, group_id)
        return len(data)    

    def get_dataset(self, view_mode, group_id):
        data = None
        if (not self.config.app) or (not self.config.role):
            return data
        data = Task.objects.filter(user=self.request.user.id)

        role_id = ROLES_IDS[self.config.role]

        if (self.config.app == 'todo'):
            data = data.filter(app_task=role_id)
        if (self.config.app == 'note'):
            data = data.filter(app_note=role_id)
        if (self.config.app == 'news'):
            data = data.filter(app_news=role_id)
        if (self.config.app == 'store'):
            data = data.filter(app_store=role_id)
        if (self.config.app == 'docs'):
            data = data.filter(app_doc=role_id)
        if (self.config.app == 'warr'):
            data = data.filter(app_warr=role_id)
        if (self.config.app == 'expen'):
            data = data.filter(app_expen=role_id)
        if (self.config.app == 'trip'):
            data = data.filter(app_trip=role_id)
        if (self.config.app == 'fuel'):
            data = data.filter(app_fuel=role_id)
        if (self.config.app == 'apart'):
            data = data.filter(app_apart=role_id)
        if (self.config.app == 'health'):
            data = data.filter(app_health=role_id)
        if (self.config.app == 'work'):
            data = data.filter(app_work=role_id)
        if (self.config.app == 'photo'):
            data = data.filter(app_photo=role_id)

        if data and (view_mode == 'by_group') and group_id:
            data = data.filter(groups__id=group_id)
        
        return self.tune_dataset(data, view_mode)

class BaseListView(CreateView, Context):

    def __init__(self, config, cur_role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(config, cur_role)
        self.template_name = 'base/list.html'

    def get_queryset(self):
        return self.get_dataset(self.config.cur_view, self.config.group_id)

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context())
        return context

class BaseDetailView(UpdateView, Context):

    def __init__(self, config, cur_role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(config, cur_role)
        self.template_name = config['name'] + '/' + self.config.role + '.html'

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context())
        context['title'] = self.object.name
        return context

    def get_doc(request, pk, fname):
        pass
        """
        path = get_file_storage_path(request.user, pk)
        try:
            fsock = open(path + fname, 'rb')
            return FileResponse(fsock)
        except IOError:
            response = HttpResponseNotFound()
        """

class BaseGroupView(UpdateView, Context):
    model = Group
    template_name = 'base/group_detail.html'
    form_class = GroupForm

    def __init__(self, config, cur_role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(config, cur_role)

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context())
        return context
