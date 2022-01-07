from task.const import *

app_config = {
    'name': APP_HEALTH,
    'app_title': 'health',
    'icon': 'star',
    'main_view': 'biomarker',
    'sort': [
        ('name', 'name'),
    ],
    'views': {
        'biomarker': {
            'role': ROLE_MARKER,
            'icon': 'heart', 
            'title': 'biomarkers',
            'paginator': 10,
            'hide_qty': True,
        },
        'chart': {
            'icon': 'graph-up', 
            'title': 'charts',
            'hide_qty': True,
        },
        'incident': {
            'role': ROLE_INCIDENT,
            'icon': 'thermometer-half', 
            'title': 'incidents',
            'hide_qty': True,
        },
    }
}

