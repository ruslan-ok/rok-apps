from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FuelConfig(AppConfig):
    name = 'v2_fuel'
    verbose_name = _('fuelings')
