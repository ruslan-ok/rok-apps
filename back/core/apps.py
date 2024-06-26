from django.apps import AppConfig
from django.utils.translation import gettext


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    app_config = {
        'icon': 'house-door',
        'href': '/',
        'permission': '',
        'order': 1,
        'human_name': gettext('Home'),
    }
