from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_LOGS,
    'app_title': _('logs'),
    'icon': 'card-list',
    'role': ROLE_LOGS,
    'main_view': 'background',
    'sort': [
        ('event', _('event date')),
        ('name', _('name')),
    ],
    'views': {
        'background': {
            'icon': 'card-list',
            'title': _('Service background process'),
            'hide_qty': True,
        },
        'backup': {
            'icon': 'card-list',
            'title': _('Backup check'),
            'hide_qty': True,
        },
        'apache': {
            'icon': 'card-list',
            'title': _('Apache logs analyzer'),
            'hide_qty': True,
            'hide_on_host': 'localhost',
        },
        'notification': {
            'icon': 'card-list',
            'title': _('Notification report'),
            'hide_qty': True,
            'hide_on_host': 'localhost',
        },
        'intervals': {
            'icon': 'card-list',
            'title': _('Service intervals control'),
            'hide_qty': True,
        },
        'versions': {
            'icon': 'card-list',
            'title': _('Software versions'),
            'hide_qty': True,
        },
    }
}

