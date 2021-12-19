from task.const import *

app_config = {
    'name': APP_STORE,
    'app_title': 'passwords',
    'icon': 'key',
    'role': ROLE_STORE,
    'main_view': 'all',
    'use_groups': True,
    'sort': [
        ('name', 'name'),
    ],
    'views': {
        'all': {
            'icon': 'infinity',
            'title': 'all',
        },
        'params': {
            'page_url': 'params',
            'icon': 'gear', 
            'title': 'default parameters',
            'hide_qty': True,
        },
    }
}

