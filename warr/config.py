from task.const import *

app_config = {
    'name': APP_WARR,
    'app_title': 'warranties',
    'icon': 'award',
    'main_view': 'all',
    'use_groups': True,
    'sort': [
        ('name', 'name'),
    ],
    'views': {
        'all': {
            'role': ROLE_WARR,
            'icon': 'award', 
            'title': 'warranties',
        },
    }
}

