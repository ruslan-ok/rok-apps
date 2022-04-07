from task.const import *

app_config = {
    'name': APP_GENEA,
    'app_title': 'family tree',
    'icon': 'diagram-3',
    'main_view': 'events',
    'sort': [
        ('name', 'name'),
    ],
    'views': {
        'events': {
            'icon': 'diagram-3', 
            'title': 'family tree',
            'sort': [
                ('event', 'event date'),
            ],
        },
        'statistics': {
            'icon': 'diagram-3', 
            'title': 'family tree',
        },
        'tree': {
            'icon': 'diagram-3', 
            'title': 'family tree',
        },
        'photo': {
            'icon': 'diagram-3', 
            'title': 'family tree',
        },
    }
}

