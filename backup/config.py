from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_BACKUP,
    'app_title': _('backup check'),
    'icon': 'bootstrap',
    'main_view': 'check',
    'sort': [
        ('event', _('event date')),
        ('name', _('name')),
    ],
    'views': {
        'check': {
            'icon': 'bootstrap',
            'title': _('backup check'),
            'role': ROLE_BACKUP,
            'hide_qty': True,
        },
    }
}

