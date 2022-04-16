from task.const import *

app_config = {
    'name': APP_FAMILY,
    'role': ROLE_STEMMA,
    'app_title': 'family tree',
    'icon': 'diagram-3',
    'main_view': 'tree',
    'views': {
        'tree': {
            'icon': 'diagram-3', 
            'title': 'stemma',
        },
        'chart_family': {
            'icon': 'diagram-3', 
            'title': 'family',
        },
        'chart_ancestors': {
            'icon': 'diagram-3', 
            'title': 'ancestors',
        },
    }
}

