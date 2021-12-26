from task.const import *

app_config = {
    'name': APP_FUEL,
    'app_title': 'fueling',
    'icon': 'truck',
    'main_view': 'fueling',
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
            'title': 'itnervals',
        },
        'service': {
            'role': ROLE_SERVICE,
            'icon': 'tools', 
            'title': 'services',
        },
        'car': {
            'role': ROLE_CAR,
            'icon': 'truck', 
            'title': 'cars',
        },
    }
}

