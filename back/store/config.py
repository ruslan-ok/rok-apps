from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_STORE,
    'app_title': _('passwords'),
    'icon': 'key',
    'role': ROLE_STORE,
    'role_loc': pgettext_lazy('add ... ', 'password'),
    'main_view': 'actual',
    'use_groups': True,
    'use_selector': True,
    'sort': [
        ('name', _('name')),
        ('created', _('create date')),
    ],
    'views': {
        'actual': {
            'icon': 'key',
            'title': _('Actual'),
        },
        'completed': {
            'icon': 'check2-circle',
            'title': _('Unactual'),
        },
        'all': {
            'icon': 'infinity',
            'title': _('All'),
            'use_sub_groups': True,
            # 'hide_qty': True,
        },
        'params': {
            'page_url': 'params',
            'icon': 'gear', 
            'title': _('Default parameters'),
            'hide_qty': True,
        },
    }
}

