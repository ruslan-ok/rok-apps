from task.const import *

app_config = {
    'name': APP_PHOTO,
    'app_title': 'photo bank',
    'icon': 'image',
    'main_view': 'root',
    'use_groups': True,
    'sort': [
        ('name', 'name'),
    ],
    'views': {
        'root': {
            'role': ROLE_PHOTO,
            'icon': 'image', 
            'title': 'all photos',
        },
    }
}

