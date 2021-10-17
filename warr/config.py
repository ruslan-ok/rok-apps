from task.const import *

app_config = {
    'name': APP_WARR,
    'title': 'warranties',
    'icon': 'star',
    'roles': {
        'warr': { 
            'icon': 'star', 
            'groups': True,
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

