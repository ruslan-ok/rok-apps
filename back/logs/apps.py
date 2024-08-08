from django.apps import AppConfig
from django.utils.translation import gettext, gettext_lazy as _

from task.const import APP_LOGS

class LogsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'logs'
    app_config = {
        'name': APP_LOGS,
        'app_title': _('logs'),
        'human_name': gettext('Logs'),
        'icon': 'card-list',
        'permission': 'task.view_logs',
        'order': 15,
        'role': 'apache',
        'main_view': 'backup_check',
        'sort': [
            ('event', _('event date')),
            ('name', _('name')),
        ],
        'views': {
            'backup_check': {
                'icon': 'save',
                'title': _('Backup check'),
                'hide_qty': True,
            },
            'versions': {
                'icon': 'card-list',
                'title': _('Software versions'),
                'hide_qty': True,
            },
        }
    }

