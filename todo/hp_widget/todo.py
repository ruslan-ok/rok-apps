import os
from datetime import datetime, timedelta
from django.db.models import Q
from rusel.base.views import BaseListView
from task.const import NUM_ROLE_TODO, ROLE_ACCOUNT
from task.models import TaskInfo
from rusel.config import app_config

class ListView(BaseListView):
    model = TaskInfo
    fields = {'name'}

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, ROLE_ACCOUNT, *args, **kwargs)

    def get_queryset(self):
        data = super().get_queryset()
        if data:
            lookups = Q(stop__lte=(datetime.now() + timedelta(1))) | Q(in_my_day=True) | Q(important=True)
            svc_grp_id = int(os.environ.get('DJANGO_SERVICE_GROUP', '0'))
            return data.filter(num_role=NUM_ROLE_TODO).filter(lookups).exclude(completed=True).exclude(group_id=svc_grp_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

def get_todo(request):
    lv = ListView()
    lv.request = request
    lv.object_list = lv.get_queryset()
    if not lv.object_list or len(lv.object_list) == 0:
        return 'hide', {}
    context = lv.get_context_data()
    template_name = 'hp_widget/todo.html'
    return template_name, context
