from core.views import BaseListView
from task.const import APP_HOME
from task.models import Task
from logs.services.overview import OverviewLogData

class ListView(BaseListView):
    model = Task
    fields = {'name'}

    def __init__(self):
        super().__init__(APP_HOME)

    def get_queryset(self):
        return []

    def get_context_data(self):
        context = super().get_context_data()
        ov = OverviewLogData()
        context['health'] = ov.get_health(5)
        return context
