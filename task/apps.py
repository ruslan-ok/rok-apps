from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TaskConfig(AppConfig):
    name = 'task'
    verbose_name = _('tasks')
