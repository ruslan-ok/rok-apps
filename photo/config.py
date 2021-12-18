from task.const import *

app_config = {
    'name': APP_PHOTO,
    'app_title': 'photo bank',
    'icon': 'star',
    'role': ROLE_PHOTO,
    'use_groups': True,
    'group_entity': 'folder',
    'sort': [
        ('name', 'name'),
    ],
    'views': {
        'all': {
            'icon': 'star', 
            'title': 'all photos',
        },
    }
}

