from task.const import *

app_config = {
    'name': APP_APART,
    'app_title': 'communal',
    'icon': 'building',
    'main_view': 'apart',
    'group_entity': 'apart',
    'sort': [
        ('name', 'name'),
        ('created', 'create date'),
    ],
    'views': {
        'apart': {
            'role': ROLE_APART,
            'icon': 'building', 
            'title': 'apartments',
            'item_name': 'apartment',
        },
        'meter': {
            'role': ROLE_METER,
            'icon': 'speedometer2', 
            'title': 'meters data',
            'item_name': 'meters data',
            'add_button': True,
            'relate': [ROLE_TODO],
        },
        'service': {
            'role': ROLE_SERVICE,
            'icon': 'tools', 
            'title': 'services',
        },
        'price': {
            'role': ROLE_PRICE,
            'icon': 'tag', 
            'title': 'prices',
            'add_button': True,
        },
        'bill': {
            'role': ROLE_BILL,
            'icon': 'receipt', 
            'title': 'bills',
            'add_button': True,
            'relate': [ROLE_TODO],
       },
    }
}