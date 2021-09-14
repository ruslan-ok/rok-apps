from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from rusel.context import get_base_context
from rusel.apps import get_app_by_role
from task.forms import GroupForm
from task.const import ROLES_IDS
from task.models import Task, Group, TaskGroup

class Context:
    def set_config(self, config, role):
        self.config = config
        self.role = role
        self.app = get_app_by_role(role)

    def get_app_context(self, **kwargs):
        self.view_mode = 'all'
        self.group_id = 0
        self.query = None
        if self.request.method == 'GET':
            if ('view' in self.request.GET):
                self.view_mode = self.request.GET.get('view')
            if (self.view_mode == 'by_group') and ('group_id' in self.request.GET):
                self.group_id = int(self.request.GET.get('group_id'))

        role_cfg = self.config['roles'][self.role]
        if (self.view_mode in role_cfg['views']):
            view_cfg = role_cfg['views'][self.view_mode]
        else:
            if (self.view_mode == 'by_group'):
                view_cfg = {
                    'url': 'group',
                    'icon': self.config['icon'],
                    'title': '???',
                }
        context = {}
        title = _(view_cfg['title']).capitalize()
        context.update(get_base_context(self.request, self.role, False, title))
        context['content_icon'] = view_cfg['icon']
        common_url = reverse(self.config['name'] + ':list')
        fixes = []
        views = role_cfg['views']
        for key, value in views.items():
            if (key == 'by_group'):
                continue
            url = common_url
            if value['url']:
                url += '?view=' + value['url']
            qty = self.get_qty(key, 0)
            fixes.append({'name': key, 'url': url, 'icon': value['icon'], 'title': _(value['title']).capitalize(), 'qty': qty})
        context['fix_list'] = fixes
        #context['group_form'] = CreateGroupForm()
        #context['sort_options'] = self.get_sorts()
        #context['params'] = extract_get_params(self.request)
        context['item_detail_url'] = self.config['name'] + ':item'
        context['use_selector'] = role_cfg.get('use_selector', False)
        context['use_important'] = role_cfg.get('use_important', False)

        groups = []
        query = None
        page_number = 1
        if self.request.method == 'GET':
            query = self.request.GET.get('q')
            page_number = self.request.GET.get('page')
            if not page_number:
                page_number = 1
        search_mode = 0
    
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
        #----------------------------
        return context

    def get_info(self, item):
        return []

    def get_qty(self, view_mode, group_id):
        data = self.get_dataset(view_mode, group_id)
        return len(data)    

    def get_dataset(self, view_mode, group_id):
        data = None
        if (not self.app) or (not self.role):
            return data
        data = Task.objects.filter(user=self.request.user.id)

        role_id = ROLES_IDS[self.role]

        if (self.app == 'todo'):
            data = data.filter(app_task=role_id)
        if (self.app == 'note'):
            data = data.filter(app_note=role_id)
        if (self.app == 'news'):
            data = data.filter(app_news=role_id)
        if (self.app == 'store'):
            data = data.filter(app_store=role_id)
        if (self.app == 'docs'):
            data = data.filter(app_doc=role_id)
        if (self.app == 'warr'):
            data = data.filter(app_warr=role_id)
        if (self.app == 'expen'):
            data = data.filter(app_expen=role_id)
        if (self.app == 'trip'):
            data = data.filter(app_trip=role_id)
        if (self.app == 'fuel'):
            data = data.filter(app_fuel=role_id)
        if (self.app == 'apart'):
            data = data.filter(app_apart=role_id)
        if (self.app == 'health'):
            data = data.filter(app_health=role_id)
        if (self.app == 'work'):
            data = data.filter(app_work=role_id)
        if (self.app == 'photo'):
            data = data.filter(app_photo=role_id)

        if data and (view_mode == 'by_group') and group_id:
            data = data.filter(groups__id=group_id)
        
        return self.tune_dataset(data, view_mode)

class BaseListView(CreateView, Context):

    def __init__(self, config, role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(config, role)
        """
        if (config['view_as_tree']):
            self.template_name = 'base/tree.html'
        else:
            self.template_name = 'base/list.html'
        """
        self.template_name = 'base/list.html'

    def get_queryset(self):
        return self.get_dataset(self.view_mode, self.group_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context())
        return context

class BaseDetailView(UpdateView, Context):

    def __init__(self, config, role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(config, role)
        self.template_name = config['name'] + '/item.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context())
        context['title'] = self.object.name
        context['content_icon'] = self.config['roles'][self.role]['icon']
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

    def __init__(self, config, role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(config, role)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context())
        return context
