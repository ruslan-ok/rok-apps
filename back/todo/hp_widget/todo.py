import os
from datetime import datetime, timedelta
from django.db.models import Q
from core.views import BaseListView
from task.const import NUM_ROLE_TODO, ROLE_TODO, ROLE_ACCOUNT
from task.models import TaskInfo, Task, Step
from rusel.config import app_config
from rusel.settings import ENV, DB

class ListView(BaseListView):
    model = TaskInfo
    fields = {'name'}

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, ROLE_ACCOUNT, *args, **kwargs)

    def get_queryset(self):
        data = super().get_queryset()
        if data:
            lookups = Q(stop__lte=(datetime.now() + timedelta(1))) | Q(in_my_day=True) | Q(important=True)
            svc_grp_id = int(os.environ.get('DJANGO_SERVICE_GROUP' + ENV + DB, '0'))
            return data.filter(num_role=NUM_ROLE_TODO).filter(lookups).exclude(completed=True).exclude(group_id=svc_grp_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

def get_todo(request):
    lookups = Q(stop__lte=(datetime.now() + timedelta(1))) | Q(in_my_day=True) | Q(important=True)
    svc_grp_id = int(os.environ.get('DJANGO_SERVICE_GROUP' + ENV + DB, '0'))
    tasks = Task.objects.filter(user=request.user.id, app_task=NUM_ROLE_TODO).filter(lookups).exclude(completed=True).exclude(groups=svc_grp_id)
    data = [{ 
        'id': x.id, 
        'stop': x.stop, 
        'name': x.name, 
        'url': x.get_absolute_url(), 
        'group': x.get_group_name(ROLE_TODO),
        'completed': x.completed,
        'in_my_day': x.in_my_day,
        'important': x.important,
        'remind': x.remind,
        'repeat': x.repeat,
        'repeat_num': x.repeat_num,
        'repeat_days': x.repeat_days,
        'categories': x.categories,
        'info': x.info,
        'steps': get_steps(x.id),
    } for x in tasks]
    return {'result': 'ok', 'data': data, 'title': 'Actual tasks'}

def get_steps(todo_id) -> list:
    ret = []
    for step in Step.objects.filter(task=todo_id):
        ret.append({
            'id': step.id,
            'created': step.created,
            'name': step.name,
            'sort': step.sort,
            'completed': step.completed,
        })
    return ret
