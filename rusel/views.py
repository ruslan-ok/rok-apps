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
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hp_widgets = []
        # hp_widgets.append({'id': 'todo', 'css': 'todo', 'js': 'todo', })
        # hp_widgets.append({'id': 'visited', 'css': 'info-table', })
        if (self.request.user.username == 'ruslan.ok'):
            # hp_widgets.append({'id': 'logs', 'css': 'info-table', })
            # hp_widgets.append({'id': 'weather'})
            # hp_widgets.append({'id': 'crypto'})
            # hp_widgets.append({'id': 'currency'})
            hp_widgets.append({'id': 'health', 'js': 'health', })
        context['hp_widgets'] = hp_widgets
        return context

def get_doc(request, role, pk, fname):
    return get_app_doc(request, role, pk, fname)

def get_thumbnail(request, role, pk, fname):
    return get_app_thumbnail(request, role, pk, fname)

