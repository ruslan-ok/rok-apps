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
        'background': {
            'icon': 'fast-forward',
            'title': _('Service manager'),
            'hide_qty': True,
        },
        'backup_nuc_short': {
            'icon': 'save',
            'title': _('Backup Nuc short log'),
            'hide_qty': True,
        },
        'backup_nuc_full': {
            'icon': 'save-fill',
            'title': _('Backup Nuc full log'),
            'hide_qty': True,
        },
        'backup_nuc_check': {
            'icon': 'card-list',
            'title': _('Backup Nuc check'),
            'hide_qty': True,
        },
        'backup_vivo_short': {
            'icon': 'save',
            'title': _('Backup Vivo short log'),
            'hide_qty': True,
        },
        'backup_vivo_full': {
            'icon': 'save-fill',
            'title': _('Backup Vivo full log'),
            'hide_qty': True,
        },
        'backup_vivo_check': {
            'icon': 'card-list',
            'title': _('Backup Vivo check'),
            'hide_qty': True,
        },
        'notification': {
            'icon': 'bell',
            'title': _('Task notification report'),
            'hide_qty': True,
            #'hide_on_host': 'localhost',
        },
        'intervals': {
            'icon': 'tools',
            'title': _('Service intervals control'),
            'hide_qty': True,
        },
        'apache': {
            'icon': 'server',
            'title': _('Apache log analyzer'),
            'hide_qty': True,
            #'hide_on_host': 'localhost',
        },
        'versions': {
            'icon': 'card-list',
            'title': _('Software versions'),
            'hide_qty': True,
        },
    }
}

