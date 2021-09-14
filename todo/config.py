app_config = {
    'name': 'todo',
    'title': 'tasks',
    'icon': 'check2-square',
    'roles': {
        'todo': {
            'icon': 'check2-square', 
            'groups': True,
            'use_selector': True,
            'use_important': True,
            'views': {
                'myday': {
                    'url': 'myday',
                    'icon': 'sun',
                    'title': 'my day',
                },
                'important': {
                    'url': 'important',
                    'icon': 'star',
                    'title': 'important',
                },
                'planned': {
                    'url': 'planned',
                    'icon': 'check2-square',
                    'title': 'planned',
                },
                'all': {
                    'url': '',
                    'icon': 'check-all',
                    'title': 'all',
                },
                'completed': {
                    'url': 'completed',
                    'icon': 'check2-circle',
                    'title': 'completed',
                },
            }
        },
    }
}