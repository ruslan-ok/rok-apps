from task.const import *

app_config = {
    'name': APP_DOCS,
    'app_title': 'documents',
    'icon': 'file-text',
    'main_view': 'all',
    'use_groups': True,
    'group_entity': 'folder',
    'sort': [
        ('name', 'name'),
    ],
    'views': {
        'all': {
            'role': ROLE_DOC,
            'icon': 'file-text', 
            'title': 'documents',
        },
    }
}

