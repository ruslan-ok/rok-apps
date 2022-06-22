from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_NEWS,
    'app_title': _('news'),
    'icon': 'newspaper',
    'role': ROLE_NEWS,
    'role_loc': pgettext_lazy('add ... ', 'news'),
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

