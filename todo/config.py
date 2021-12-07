from task.const import *

app_config = {
    'name': APP_TODO,
    'app_title': 'tasks',
    'icon': 'check2-square',
    'role': ROLE_TODO,
    'use_groups': True,
    'use_selector': True,
    'use_important': True,
    'sort': [
        ('important', 'important'),
        ('stop', 'termin'),
        ('name', 'name'),
        ('created', 'create date'),
    ],
    'views': {
        'todo': {
            'icon': 'sun',
            'title': 'my day',
        },
        'important': {
            'icon': 'star',
            'title': 'important tasks',
            'sort': [
                ('stop', 'termin'),
                ('name', 'name'),
                ('created', 'create date'),
            ],
        },
        'planned': {
            'icon': 'check2-square',
            'title': 'planned tasks',
            'sort': [
                ('important', 'important'),
                ('name', 'name'),
                ('created', 'create date'),
            ],
        },
        'all': {
            'icon': 'check-all',
            'title': 'all',
        },
        'completed': {
            'icon': 'check2-circle',
            'title': 'completed tasks',
        },
    }
}