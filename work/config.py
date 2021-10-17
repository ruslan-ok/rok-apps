from task.const import *

app_config = {
    'name': APP_WORK,
    'title': 'work',
    'icon': 'star',
    'roles': {
        'work': { 
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
