from task.const import *

app_config = {
    'name': APP_WARR,
    'app_title': 'warranties',
    'icon': 'award',
    'main_view': 'active',
    'use_groups': True,
    'role': ROLE_WARR,
    'sort': [
        ('stop', 'termin'),
        ('name', 'name'),
    ],
    'views': {
        'active': {
            'icon': 'award', 
            'title': 'active warranties',
        },
        'expired': {
            'icon': 'award', 
            'title': 'expired warranties',
        },
        'all': {
            'icon': 'award', 
            'title': 'all warranties',
        },
    }
}

