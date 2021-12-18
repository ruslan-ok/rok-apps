from task.const import *

app_config = {
    'name': APP_DOCS,
    'app_title': 'documents',
    'icon': 'star',
    'role': ROLE_DOC,
    'use_groups': True,
    'group_entity': 'folder',
    'sort': [
        ('name', 'name'),
    ],
    'views': {
        'all': {
            'icon': 'star', 
            'title': 'documents',
        },
    }
}

