from task.const import *

app_config = {
    'name': APP_STORE,
    'app_title': 'passwords',
    'icon': 'key',
    'role': ROLE_STORE,
    'use_groups': True,
    'sort': [
        ('name', 'name'),
    ],
    'views': {
        'store': {
            'icon': 'check-all',
            'title': 'all',
        },
    }
}

