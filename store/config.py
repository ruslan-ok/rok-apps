from task.const import *

app_config = {
    'name': APP_STORE,
    'app_title': 'passwords',
    'icon': 'key',
    'main_view': 'all',
    'use_groups': True,
    'sort': [
        ('name', 'name'),
    ],
    'views': {
        'all': {
            'role': ROLE_STORE,
            'icon': 'infinity',
            'title': 'all',
        },
        'params': {
            'role': ROLE_PARAMS,
            'icon': 'gear', 
            'title': 'default parameters',
            'hide_qty': True,
        },
    }
}

