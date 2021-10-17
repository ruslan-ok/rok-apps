from task.const import *

app_config = {
    'name': APP_HEALTH,
    'title': 'health',
    'icon': 'star',
    'roles': {
        'health': { 
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

