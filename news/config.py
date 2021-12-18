from task.const import *

app_config = {
    'name': APP_NEWS,
    'app_title': 'news',
    'icon': 'newspaper',
    'role': ROLE_NEWS,
    'use_groups': True,
    'sort': [
        ('event', 'event date'),
        ('name', 'name'),
    ],
    'views': {
        'news': {
            'icon': 'infinity',
            'title': 'all',
        },
    }
}

