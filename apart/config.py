from task.const import *

app_config = {
    'name': APP_APART,
    'app_title': 'communal',
    'icon': 'building',
    'main_view': 'bill',
    'group_entity': 'apart',
    'views': {
        'bill': {
            'role': ROLE_BILL,
            'icon': 'receipt', 
            'title': 'bills',
            'add_button': True,
            'relate': [ROLE_TODO],
            'sort': [
                ('name', 'name'),
                ('start', 'period'),
            ],
       },
        'meter': {
            'role': ROLE_METER,
            'icon': 'speedometer2', 
            'title': 'meters data',
            'item_name': 'meters data',
            'add_button': True,
            'relate': [ROLE_TODO],
            'sort': [
                ('name', 'name'),
                ('start', 'period'),
            ],
        },
        'price': {
            'role': ROLE_PRICE,
            'icon': 'tag', 
            'title': 'prices',
            'add_button': True,
            'use_sub_groups': True,
            'sort': [
                ('name', 'name'),
                ('start', 'valid from'),
            ],
        },
        'apart': {
            'role': ROLE_APART,
            'icon': 'building', 
            'title': 'apartments',
            'item_name': 'apartment',
            'sort': [
                ('name', 'name'),
                ('sort', 'sort code'),
            ],
        },
    }
}