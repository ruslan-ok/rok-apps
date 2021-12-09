from task.const import *

app_config = {
    'name': APP_EXPEN,
    'app_title': 'expenses',
    'icon': 'star',
    'role': ROLE_PROJECT,
    'sort': [
        ('name', 'name'),
    ],
    'views': {
        'project': {
            'icon': 'star', 
            'title': 'projects',
            'url': 'project',
            'use_selector': True,
        },
        'expense': {
            'role': ROLE_EXPENSE,
            'icon': 'star', 
            'title': 'expenses',
        },
    }
}

