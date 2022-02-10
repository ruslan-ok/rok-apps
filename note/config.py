from task.const import *

app_config = {
    'name': APP_NOTE,
    'app_title': 'notes',
    'icon': 'sticky',
    'role': ROLE_NOTE,
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

