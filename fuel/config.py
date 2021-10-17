from task.const import *

app_config = {
    'name': APP_FUEL,
    'title': 'fueling',
    'icon': 'star',
    'views': {
        'cars': {
            'role': ROLE_APART,
            'icon': 'building', 
            'title': 'apartments',
            'use_selector': True,
        },
        'fuelings': {
            'role': ROLE_FUEL,
            'icon': 'star', 
            'url': 'services',
            'title': 'services',
        },
        'itnervals': {
            'role': ROLE_PART,
            'icon': 'star', 
            'url': 'meters',
            'title': 'meters data',
        },
        'service': {
            'role': ROLE_SERVICE,
            'icon': 'star', 
            'url': 'prices',
            'title': 'prices',
        },
    }
}

