from task.const import *

app_config = {
    'name': APP_NEWS,
    'app_title': 'news',
    'icon': 'newspaper',
    'role': ROLE_NEWS,
    'main_view': 'all',
    'use_groups': True,
    'sort': [
        ('event', 'event date'),
        ('name', 'name'),
    ],
    'views': {
        'all': {
            'icon': 'infinity',
            'title': 'all',
        },
    }
}

