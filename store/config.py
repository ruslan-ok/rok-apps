from django.utils.translation import gettext_lazy as _
from task.const import *

app_config = {
    'name': APP_STORE,
    'app_title': _('passwords'),
    'icon': 'key',
    'role': ROLE_STORE,
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
            'title': _('actual'),
        },
        'completed': {
            'icon': 'check2-circle',
            'title': _('unactual'),
        },
        'all': {
            'icon': 'infinity',
            'title': _('all'),
            'use_sub_groups': True,
            # 'hide_qty': True,
        },
        'params': {
            'page_url': 'params',
            'icon': 'gear', 
            'title': _('default parameters'),
            'hide_qty': True,
        },
    }
}

