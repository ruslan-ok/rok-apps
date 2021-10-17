from task.const import *

app_config = {
    'name': APP_EXPEN,
    'title': 'expenses',
    'icon': 'star',
    'views': {
        'projects': {
            'role': ROLE_PROJECT,
            'icon': 'star', 
            'title': 'projects',
            'url': 'projects',
            'use_selector': True,
        },
        'expenses': {
            'role': ROLE_EXPENSES,
            'icon': 'star', 
            'title': 'expenses',
        },
    }
}

