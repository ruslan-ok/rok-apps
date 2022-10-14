from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_LOGS,
    'app_title': _('logs'),
    'icon': 'card-list',
    'role': ROLE_APACHE,
    'main_view': 'overview',
    'sort': [
        ('event', _('event date')),
        ('name', _('name')),
    ],
    'views': {
        'overview': {
            'icon': 'heart',
            'title': _('All services health'),
            'hide_qty': True,
        },
        'backup_nuc_check': {
            'icon': 'card-list',
            'title': _('Backup Nuc check'),
            'hide_qty': True,
        },
        'backup_vivo_check': {
            'icon': 'card-list',
            'title': _('Backup Vivo check'),
            'hide_qty': True,
        },
        'backup_v3_vivo_check': {
            'icon': 'card-list',
            'title': _('Backup v.3 Vivo check'),
            'hide_qty': True,
        },
        'versions': {
            'icon': 'card-list',
            'title': _('Software versions'),
            'hide_qty': True,
        },
    }
}

