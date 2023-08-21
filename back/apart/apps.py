from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ApartConfig(AppConfig):
    name = 'apart'
    verbose_name = _('apart')
