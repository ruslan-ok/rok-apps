from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TripConfig(AppConfig):
    name = 'trip'
    verbose_name = _('trips')
