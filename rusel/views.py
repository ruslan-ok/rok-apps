from datetime import datetime, timedelta
from django.db.models import Q
from task.const import ROLE_ACCOUNT, NUM_ROLE_TODO
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
        data = super().get_queryset()
        if data:
            lookups = Q(stop__lte=(datetime.now() + timedelta(1))) | Q(in_my_day=True) | Q(important=True)
            return data.filter(num_role=NUM_ROLE_TODO).filter(lookups).exclude(completed=True)

def get_doc(request, role, pk, fname):
    return get_app_doc(request, role, pk, fname)

def get_thumbnail(request, role, pk, fname):
    return get_app_thumbnail(request, role, pk, fname)

