from task.const import *

app_config = {
    'name': APP_HEALTH,
    'app_title': 'health',
    'icon': 'star',
    'role': ROLE_MARKER,
    'sort': [
        ('name', 'name'),
    ],
    'views': {
        'biomarker': {
            'icon': 'star', 
            'title': 'biomarkers',
        },
        'chart': {
            'icon': 'star', 
            'title': 'charts',
        },
        'incident': {
            'role': ROLE_ANAMNESIS,
            'icon': 'star', 
            'title': 'incidents',
            'use_groups': True,
            'group_entity': 'anamnesis',
        },
    }
}

