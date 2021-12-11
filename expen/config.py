from task.const import *

app_config = {
    'name': APP_EXPEN,
    'app_title': 'expenses',
    'icon': 'star',
    'role': ROLE_EXPENSE,
    'use_groups': True,
    'event_in_name': True,
    'sort': [
        ('event', 'operation date'),
        ('name', 'name'),
    ],
    'views': {
        'all': {
            'icon': 'star', 
            'title': 'expenses',
        },
    }
}

