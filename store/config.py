from task.const import *

app_config = {
    'name': APP_STORE,
    'app_title': 'passwords',
    'icon': 'key',
    'role': ROLE_STORE,
    'main_view': 'actual',
    'use_groups': True,
    'use_selector': True,
    'sort': [
        ('name', 'name'),
        ('created', 'create date'),
    ],
    'views': {
        'actual': {
            'icon': 'key',
            'title': 'actual',
        },
        'completed': {
            'icon': 'check2-circle',
            'title': 'unactual',
        },
        'all': {
            'icon': 'infinity',
            'title': 'all',
            'use_sub_groups': True,
            # 'hide_qty': True,
        },
        'params': {
            'page_url': 'params',
            'icon': 'gear', 
            'title': 'default parameters',
            'hide_qty': True,
        },
    }
}

