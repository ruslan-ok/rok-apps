from task.const import *

app_config = {
    'name': APP_HEALTH,
    'app_title': 'health',
    'icon': 'star',
    'main_view': 'biomarker',
    'views': {
        'biomarker': {
            'role': ROLE_MARKER,
            'icon': 'heart', 
            'title': 'biomarkers',
            'limit_list': 10,
            'sort': [
                ('event', 'event date'),
            ],
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
            'sort': [
                ('name', 'name'),
                ('start', 'period'),
            ],
        },
    }
}

