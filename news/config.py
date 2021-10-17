from task.const import *

app_config = {
    'name': APP_NEWS,
    'app_title': 'news',
    'icon': 'newspaper',
    'role': ROLE_NEWS,
    'groups': True,
    'views': {
        'news': {
            'icon': 'check-all',
            'title': 'all',
        },
    }
}

