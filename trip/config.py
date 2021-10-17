from task.const import *

app_config = {
    'name': APP_TRIP,
    'title': 'trips',
    'icon': 'star',
    'roles': {
        'trip': { 
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

