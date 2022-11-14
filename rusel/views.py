import json
from datetime import datetime, timedelta
from django.db.models import Q
from task.const import ROLE_ACCOUNT, NUM_ROLE_TODO
from task.models import Task, VisitedHistory
from logs.services.overview import OverviewLogData
from health.views.chart import build_weight_chart
from rusel.base.views import BaseListView
from rusel.context import MAX_LAST_VISITED
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if (self.request.user.username == 'ruslan.ok'):
            context['last_visited'] = VisitedHistory.objects.filter(user=self.request.user.id).order_by('-stamp')[:MAX_LAST_VISITED]
            ov = OverviewLogData()
            context['health'] = ov.get_health(5)
            data = build_weight_chart(self.request.user, compact=True)
            s_data = json.dumps(data)
            context['chart_data'] = s_data
        return context

def get_doc(request, role, pk, fname):
    return get_app_doc(request, role, pk, fname)

def get_thumbnail(request, role, pk, fname):
    return get_app_thumbnail(request, role, pk, fname)

