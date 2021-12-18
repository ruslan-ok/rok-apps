from task.const import *

app_config = {
    'name': APP_APART,
    'app_title': 'communal',
    'icon': 'building',
    'role': ROLE_METER,
    'use_groups': True,
    'group_entity': 'apart',
    'sort': [
        ('name', 'name'),
        ('created', 'create date'),
    ],
    'views': {
        'meter': {
            'icon': 'star', 
            'title': 'meters data',
            'item_name': 'meters data',
            'add_button': True,
            'relate': [ROLE_TODO],
        },
        'service': {
            'role': ROLE_SERVICE,
            'icon': 'star', 
            'title': 'services',
        },
        'price': {
            'role': ROLE_PRICE,
            'icon': 'star', 
            'title': 'prices',
            'add_button': True,
        },
        'bill': {
            'role': ROLE_BILL,
            'icon': 'star', 
            'title': 'bills',
            'add_button': True,
            'relate': [ROLE_TODO],
       },
    }
}