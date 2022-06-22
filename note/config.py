from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_NOTE,
    'app_title': _('notes'),
    'icon': 'sticky',
    'role': ROLE_NOTE,
    'role_loc': pgettext_lazy('add ... ', 'note'),
    'main_view': 'all',
    'use_groups': True,
    'sort': [
        ('event', _('event date')),
        ('name', _('name')),
    ],
    'views': {
        'all': {
            'icon': 'infinity',
            'title': _('all'),
        },
    }
}

