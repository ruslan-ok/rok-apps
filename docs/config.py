from task.const import *

app_config = {
    'name': APP_DOCS,
    'app_title': 'documents',
    'icon': 'file-text',
    'main_view': 'root',
    'use_groups': True,
    'sort': [
        ('name', 'name'),
    ],
    'views': {
        'root': {
            'role': ROLE_DOC,
            'icon': 'file-text', 
            'title': 'documents',
        },
    }
}

