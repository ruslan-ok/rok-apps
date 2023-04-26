from task.const import ROLE_ACCOUNT
from task.models import Task
from rusel.base.views import BaseListView
from rusel.config import app_config
from rusel.app_doc import get_app_doc, get_app_thumbnail

class ListView(BaseListView):
    model = Task
    fields = {'name'}

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, ROLE_ACCOUNT, *args, **kwargs)

    def get_template_names(self):
        if not self.request.user.is_authenticated:
            return ['index_anonim.html']

        query = None
        if (self.request.method == 'GET'):
            query = self.request.GET.get('q')
        if query:
            return ['base/list.html']
        
        return ['index_user.html']

    def get_queryset(self):
        query = None
        if (self.request.method == 'GET'):
            query = self.request.GET.get('q')
        if query:
            return super().get_queryset()
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hp_widgets = []
        for hpw in HP_WIDGETS:
            id = hpw[0]
            css = hpw[1]
            js = hpw[2]
            perm = hpw[3]
            if perm and not self.request.user.has_perm(perm):
                continue
            if perm and self.request.user.is_superuser:
                continue
            hp_widgets.append({'id': id, 'css': css, 'js': js, })
        context['hp_widgets'] = hp_widgets
        return context
    
HP_WIDGETS = [
    ('weather', 'weather', '', ''),
    #('currency', 'currency', '', ''),
    ('crypto', 'crypto', '', 'task.view_entry'),
    ('health', '', '', 'task.view_health'),
    ('logs', 'logs', '', 'task.view_logs'),
    ('todo', 'todo', 'todo', 'task.view_todo'),
    ('visited', 'visited', '', ''),
]

def get_doc(request, role, pk, fname):
    return get_app_doc(request, role, pk, fname)

def get_thumbnail(request, role, pk, fname):
    return get_app_thumbnail(request, role, pk, fname)

