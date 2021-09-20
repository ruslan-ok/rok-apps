from task.const import *

app_config = {
    'name': 'expen',
    'title': 'expenses',
    'icon': 'star',
    'views': {
        'projects': {
            'role': ROLE_EXPEN_PROJ,
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

