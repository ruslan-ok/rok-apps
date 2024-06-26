from django.apps import AppConfig
from django.utils.translation import gettext


class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'
    app_config = {
        'icon': 'people',
        'href': '/admin/',
        'permission': 'task.administrate_site',
        'order': 16,
        'human_name': gettext('Admin'),
    }
