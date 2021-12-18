from task.const import *

app_config = {
    'name': APP_WARR,
    'app_title': 'warranties',
    'icon': 'star',
    'role': ROLE_WARR,
    'use_groups': True,
    'sort': [
        ('name', 'name'),
    ],
    'views': {
        'all': {
            'icon': 'star', 
            'title': 'warranties',
        },
    }
}

