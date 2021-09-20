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
            'use_selector': True,
        },
        'services': {
            'role': ROLE_APART_SERV,
            'icon': 'star', 
            'title': 'services',
        },
        'meters': {
            'role': ROLE_APART_METER,
            'icon': 'star', 
            'title': 'meters data',
        },
        'prices': {
            'role': ROLE_APART_PRICE,
            'icon': 'star', 
            'title': 'prices',
        },
        'bills': {
            'role': ROLE_APART_BILL,
            'icon': 'star', 
            'title': 'bills',
        },
    }
}