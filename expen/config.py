from task.const import *

app_config = {
    'name': APP_EXPEN,
    'app_title': 'expenses',
    'icon': 'cash-coin',
    'role': ROLE_EXPENSE,
    'main_view': 'all',
    'use_groups': True,
    'group_entity': 'project',
    'event_in_name': True,
    'sort': [
        ('event', 'operation date'),
        ('name', 'name'),
    ],
    'views': {
        'all': {
            'icon': 'infinity', 
            'title': 'all expenses',
        },
    }
}

