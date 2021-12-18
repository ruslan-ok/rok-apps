from task.const import *

app_config = {
    'name': APP_FUEL,
    'app_title': 'fueling',
    'icon': 'star',
    'role': ROLE_FUEL,
    'use_groups': True,
    'group_entity': 'person',
    'sort': [
        ('event', 'fueling date'),
    ],
    'views': {
        'fuelings': {
            'icon': 'star', 
            'title': 'fuelings',
        },
        'itnervals': {
            'role': ROLE_PART,
            'icon': 'star', 
            'url': 'itnerval',
            'title': 'itnervals',
        },
        'services': {
            'role': ROLE_SERVICE,
            'icon': 'star', 
            'url': 'service',
            'title': 'services',
        },
    }
}

