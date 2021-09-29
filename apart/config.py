from task.const import *

app_config = {
    'name': 'apart',
    'app_title': 'communal',
    'icon': 'building',
    'role': ROLE_APART,
    'views': {
        'apart': {
            'icon': 'building', 
            'title': 'apartments',
        },
        'service': {
            'role': ROLE_SERVICE,
            'icon': 'star', 
            'title': 'services',
        },
        'meter': {
            'role': ROLE_METER,
            'icon': 'star', 
            'title': 'meters data',
        },
        'price': {
            'role': ROLE_PRICE,
            'icon': 'star', 
            'title': 'prices',
        },
        'bill': {
            'role': ROLE_BILL,
            'icon': 'star', 
            'title': 'bills',
        },
    }
}