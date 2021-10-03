import os
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.http import FileResponse, HttpResponseNotFound
from django.views.generic.edit import CreateView, UpdateView
from rusel.context import get_base_context
from rusel.files import storage_path, get_files_list
from rusel.utils import extract_get_params
from task.forms import GroupForm, CreateGroupForm
from task.const import ROLES_IDS
from task.models import Task, Group, TaskGroup, Urls

class Config:
    def __init__(self, config, cur_view, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = config['name']
        self.app_title = _(config['app_title']).capitalize()
        self.title = config['app_title']
        self.icon = config['icon']
        self.views = config['views']
        self.base_role = config['role']
        self.role = self.base_role
        self.groups = self.check_property(config, 'groups', False)
        self.use_selector = self.check_property(config, 'use_selector', False)
        self.use_important = self.check_property(config, 'use_important', False)
        self.add_button = self.check_property(config, 'add_button', False)
        self.item_name = self.check_property(config, 'item_name', '')
        self.cur_view = ''
        if (cur_view in self.views):
            if ('role' in config['views'][cur_view]):
                self.role = config['views'][cur_view]['role']
            else:
                self.cur_view = cur_view
            self.title = self.check_property(self.views[cur_view], 'title', self.title)
            self.icon = self.check_property(self.views[cur_view], 'icon', self.icon)
            self.use_selector = self.check_property(self.views[cur_view], 'use_selector', self.use_selector)
            self.use_important = self.check_property(self.views[cur_view], 'use_important', self.use_important)
            self.add_button = self.check_property(self.views[cur_view], 'add_button', self.add_button)
            self.item_name = self.check_property(self.views[cur_view], 'item_name', self.item_name)

    def set_view(self, request):
        self.group_id = 0
        common_url = reverse(self.app + ':list')
        view_mode = request.path.split(common_url)[1].split('?')[0].split('/')[0]
        if request.method == 'GET':
            if ('view' in request.GET):
                view_mode = request.GET.get('view')
            if (view_mode == 'by_group') and ('group_id' in request.GET):
                self.group_id = int(request.GET.get('group_id'))
        if view_mode and (view_mode in self.views):
            self.cur_view = view_mode
            self.title = self.check_property(self.views[view_mode], 'title', self.title)
            self.icon = self.check_property(self.views[view_mode], 'icon', self.icon)
            self.add_button = self.check_property(self.views[view_mode], 'add_button', self.add_button)
            self.item_name = self.check_property(self.views[view_mode], 'item_name', self.item_name)
        elif (view_mode == 'by_group') :           
            self.cur_view = view_mode

    def check_property(self, config, prop, default):
        ret = default
        if (prop in config):
            ret = config[prop]
        return ret

class Context:
    def set_config(self, config, cur_view):
        self.config = Config(config, cur_view)

    def get_app_context(self, **kwargs):
        context = {}
        title = _(self.config.title).capitalize()
        context.update(get_base_context(self.request, self.config.app, self.config.role, False, title))
        context['fix_list'] = self.get_fixes(self.config.views)
        context['group_form'] = CreateGroupForm()
        #context['sort_options'] = self.get_sorts()
        if (self.config.role == self.config.base_role):
            context['item_detail_url'] = self.config.app + ':item'
        else:
            context['item_detail_url'] = self.config.app + ':' + self.config.role + '-item'
        context['config'] = self.config
        context['params'] = extract_get_params(self.request)
        return context

    def get_fixes(self, views):
        fixes = []
        common_url = reverse(self.config.app + ':list')
        for key, value in views.items():
            url = common_url
            view_role = self.config.base_role
            view_mode = ''
            if (view_role != key):
                if ('role' in value):
                    view_role = value['role']
                    url += view_role + '/'
                else:
                    view_mode = key
            if (view_mode):
                url += '?view=' + view_mode
            qty = self.get_qty(view_role, key, 0)
            fixes.append({'name': key, 'url': url, 'icon': value['icon'], 'title': _(value['title']).capitalize(), 'qty': qty})
        return fixes

    def get_qty(self, view_role, view_mode, group_id):
        data = self.get_dataset(view_role, view_mode, group_id)
        return len(data)    

    def get_dataset(self, view_role, view_mode, group_id):
        data = None
        if (not self.config.app) or (not view_role):
            return data
        data = Task.objects.filter(user=self.request.user.id)

        role_id = ROLES_IDS[self.config.app][view_role]

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
        return self.get_dataset(self.config.role, self.config.cur_view, self.config.group_id)

    def get_success_url(self):
        if (self.config.role == self.config.base_role):
            return reverse(self.config.app + ':item', args=(self.object.id,)) + extract_get_params(self.request)
        return reverse(self.config.app + ':' + self.config.role + '-item', args=(self.object.id,)) + extract_get_params(self.request)

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context())
        context['items'] = self.get_queryset()
        context['add_item_placeholder'] = '{} {}'.format(_('add').capitalize(), self.config.item_name if self.config.item_name else self.config.role)
        context['add_button'] = self.config.add_button
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        common_url = reverse(self.config.app + ':list')
        view_mode = self.request.path.split(common_url)[1].split('?')[0].split('/')[0]
        if ('view' in self.request.GET):
            view_mode = self.request.GET.get('view')
        if (view_mode == 'by_group') and ('group_id' in self.request.GET):
            group_id = int(self.request.GET.get('group_id'))
            group = Group.objects.filter(id=group_id).get()
            TaskGroup.objects.create(task=self.object, group=group, role=group.app)
        return response
    
class BaseDetailView(UpdateView, Context):

    def __init__(self, config, cur_role, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_config(config, cur_role)
        self.template_name = config['name'] + '/' + self.config.role + '.html'

    def get_success_url(self):
        if (self.config.role == self.config.base_role):
            return reverse(self.config.app + ':item', args=(self.object.id,)) + extract_get_params(self.request)
        return reverse(self.config.app + ':' + self.config.role + '-item', args=(self.object.id,)) + extract_get_params(self.request)

    def get_context_data(self, **kwargs):
        self.config.set_view(self.request)
        context = super().get_context_data(**kwargs)
        context.update(self.get_app_context())
        context['title'] = self.object.name
        context['urls'] = Urls.objects.filter(task=self.object.id)
        context['files'] = get_files_list(self.request.user, self.config.app, self.config.role, self.object.id)
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
            if not grp and TaskGroup.objects.filter(task=item.id, role=self.config.role).exists():
                TaskGroup.objects.filter(task=item.id, role=self.config.role).delete()
            if grp:
                if not TaskGroup.objects.filter(task=item.id, role=self.config.role).exists():
                    TaskGroup.objects.create(task=item, group=grp, role=grp.role)
                else:
                    tg = TaskGroup.objects.filter(task=item.id, role=self.config.role).get()
                    if (tg.group != grp):
                        tg.group = grp
                        tg.save()
        return ret

    def handle_uploaded_file(self, f, user, item_id):
        path = storage_path.format(user.id) + self.config.app + '/' + self.config.role + '_{}/'.format(item_id)
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
        return context

def get_app_doc(app, role, request, pk, fname):
    path = storage_path.format(request.user.id) + app + '/' + role + '_{}/'.format(pk)
    try:
        fsock = open(path + fname, 'rb')
        return FileResponse(fsock)
    except IOError:
        return HttpResponseNotFound()

