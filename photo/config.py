from task.const import *

app_config = {
    'name': APP_PHOTO,
    'app_title': 'photo bank',
    'icon': 'image',
    'main_view': 'all',
    'use_groups': True,
    'group_entity': 'folder',
    'sort': [
        ('name', 'name'),
    ],
    'views': {
        'all': {
            'role': ROLE_PHOTO,
            'icon': 'image', 
            'title': 'all photos',
        },
    }
}

