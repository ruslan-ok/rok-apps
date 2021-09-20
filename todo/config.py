from task.const import *

app_config = {
    'name': 'todo',
    'app_title': 'tasks',
    'icon': 'check2-square',
    'role': ROLE_TODO,
    'groups': True,
    'use_selector': True,
    'use_important': True,
    'views': {
        'todo': {
            'icon': 'sun',
            'title': 'my day',
        },
        'important': {
            'icon': 'star',
            'title': 'important tasks',
        },
        'planned': {
            'icon': 'check2-square',
            'title': 'planned tasks',
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