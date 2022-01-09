from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WageConfig(AppConfig):
    name = 'v2_wage'
    verbose_name = _('wage')
