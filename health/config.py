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
        'incident': {
            'role': ROLE_INCIDENT,
            'icon': 'thermometer-half', 
            'title': 'incidents',
            'sort': [
                ('name', 'name'),
                ('start', 'period'),
            ],
        },
        'weight': {
            'role': ROLE_CHART_WEIGHT,
            'icon': 'graph-up', 
            'title': 'weight chart',
            'hide_qty': True,
        },
        'waist': {
            'role': ROLE_CHART_WAIST,
            'icon': 'graph-up', 
            'title': 'waist chart',
            'hide_qty': True,
        },
        'temp': {
            'role': ROLE_CHART_TEMP,
            'icon': 'graph-up', 
            'title': 'temperature chart',
            'hide_qty': True,
        },
    }
}

