from task.const import *

app_config = {
    'name': APP_PHOTO,
    'app_title': 'photo bank',
    'icon': 'image',
    'main_view': 'preview',
    'use_groups': True,
    'role': ROLE_PHOTO,
    'sort': [
        ('name', 'name'),
    ],
    'views': {
        'preview': {
            'icon': 'images', 
            'title': 'photo preview',
        },
        'map': {
            'icon': 'geo-alt', 
            'title': 'on the map',
        },
    }
}

