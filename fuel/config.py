from task.const import *

app_config = {
    'name': APP_FUEL,
    'app_title': 'fueling',
    'icon': 'truck',
    'main_view': 'fueling',
    'use_groups': True,
    'group_entity': 'person',
    'sort': [
        ('event', 'fueling date'),
    ],
    'views': {
        'fueling': {
            'role': ROLE_FUEL,
            'icon': 'droplet', 
            'title': 'fuelings',
        },
        'part': {
            'role': ROLE_PART,
            'icon': 'cart', 
            'url': 'itnerval',
            'title': 'itnervals',
        },
        'service': {
            'role': ROLE_SERVICE,
            'icon': 'tools', 
            'url': 'service',
            'title': 'services',
        },
    }
}

