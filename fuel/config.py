from task.const import *

app_config = {
    'name': APP_FUEL,
    'app_title': 'fueling',
    'icon': 'truck',
    'main_view': 'fuel',
    'group_entity': 'car',
    'views': {
        'fuel': {
            'role': ROLE_FUEL,
            'icon': 'droplet', 
            'title': 'fuelings',
            'item_name': 'fueling',
            'add_button': True,
            'sort': [
                ('event', 'fueling date'),
            ],
        },
        'part': {
            'role': ROLE_PART,
            'icon': 'cart', 
            'title': 'itnervals',
            'item_name': 'service interval',
        },
        'service': {
            'role': ROLE_SERVICE,
            'icon': 'tools', 
            'title': 'services',
            'item_name': 'service',
            'add_button': True,
            'use_sub_groups': True,
            'sort': [
                ('event', 'due date'),
            ],
        },
        'car': {
            'role': ROLE_CAR,
            'icon': 'truck', 
            'title': 'cars',
            'item_name': 'car',
            'sort': [
                ('name', 'name'),
                ('start', 'date of commencement'),
            ],
        },
    }
}

