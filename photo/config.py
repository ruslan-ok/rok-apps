from task.const import *

app_config = {
    'name': APP_PHOTO,
    'title': 'photo bank',
    'icon': 'star',
    'roles': {
        'photo': { 
            'icon': 'star', 
            'groups': False,
            'views': {
                'all': {
                    'url': '',
                    'icon': 'check-all',
                    'title': 'all',
                },
            },
        },
    }
}

