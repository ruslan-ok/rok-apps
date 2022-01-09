from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProjConfig(AppConfig):
    name = 'v2_proj'
    verbose_name = _('projects')
