from core.views import BaseListView
from task.const import ROLE_ACCOUNT
from task.models import Task
from logs.services.overview import OverviewLogData
from rusel.config import app_config

class ListView(BaseListView):
    model = Task
    fields = {'name'}

    def __init__(self):
        super().__init__(app_config, ROLE_ACCOUNT)

    def get_queryset(self):
        return []

    def get_context_data(self):
        context = super().get_context_data()
        ov = OverviewLogData()
        context['health'] = ov.get_health(5)
        return context
