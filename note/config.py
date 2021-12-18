from task.const import *

app_config = {
    'name': APP_NOTE,
    'app_title': 'notes',
    'icon': 'sticky',
    'role': ROLE_NOTE,
    'use_groups': True,
    'sort': [
        ('event', 'event date'),
        ('name', 'name'),
    ],
    'views': {
        'note': {
            'icon': 'infinity',
            'title': 'all',
        },
    }
}

