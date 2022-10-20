from task.const import *

app_config = {
    'name': APP_FAMILY,
    'app_title': 'family tree',
    'icon': 'diagram-3',
    'main_view': 'tree',
    'group_entity': 'tree',
    'views': {
        'tree': {
            'icon': 'diagram-3', 
            'title': 'family tree',
            'hide_qty': True,
        },
        'people': {
            'icon': 'person', 
            'title': 'persons',
            'role': 'people',
        },
        'families': {
            'icon': 'people', 
            'title': 'families',
            'role': 'families',
        },
        'media': {
            'icon': 'image', 
            'title': 'media',
            'role': 'media',
        },
    }
}

