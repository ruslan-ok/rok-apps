app_config = {
    'name': 'fuel',
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
            'role': ROLE_APART_SERV,
            'icon': 'star', 
            'url': 'services',
            'title': 'services',
        },
        'itnervals': {
            'role': ROLE_FUEL_PART,
            'icon': 'star', 
            'url': 'meters',
            'title': 'meters data',
        },
        'service': {
            'role': ROLE_FUEL_SERV,
            'icon': 'star', 
            'url': 'prices',
            'title': 'prices',
        },
    }
    'roles': {
        'fuel': { 
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

