from task.const import *

app_config = {
    'name': APP_TRIP,
    'app_title': 'trips',
    'icon': 'star',
    'role': ROLE_TRIP,
    'use_groups': True,
    'group_entity': 'car',
    'sort': [
        ('event', 'trip date'),
        ('name', 'direction'),
    ],
    'views': {
        'all': {
            'icon': 'star', 
            'title': 'trips',
        },
    }
}

