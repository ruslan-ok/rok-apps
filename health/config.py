from task.const import *

app_config = {
    'name': APP_HEALTH,
    'app_title': 'health',
    'icon': 'star',
    'main_view': 'biomarker',
    'use_groups': True,
    'group_entity': 'incident',
    'sort': [
        ('name', 'name'),
    ],
    'views': {
        'biomarker': {
            'role': ROLE_MARKER,
            'icon': 'heart', 
            'title': 'biomarkers',
        },
        'chart': {
            'icon': 'graph-up', 
            'title': 'charts',
        },
        'incident': {
            'role': ROLE_ANAMNESIS,
            'icon': 'thermometer-half', 
            'title': 'incidents',
            'use_groups': True,
            'group_entity': 'anamnesis',
        },
    }
}

