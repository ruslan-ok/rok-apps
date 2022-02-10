from task.const import *

app_config = {
    'name': APP_TODO,
    'app_title': 'tasks',
    'icon': 'check2-square',
    'role': ROLE_TODO,
    'main_view': 'myday',
    'use_groups': True,
    'use_selector': True,
    'use_important': True,
    'sort': [
        ('stop', 'termin'),
        ('name', 'name'),
        ('created', 'create date'),
        ('completion', 'completion date'),
        ('important', 'important'),
        ('in_my_day', 'my day'),
    ],
    'views': {
        'myday': {
            'icon': 'sun',
            'title': 'my day',
            'sort': [
                ('stop', 'termin'),
                ('name', 'name'),
                ('created', 'create date'),
                ('important', 'important'),
            ],
        },
        'important': {
            'icon': 'star',
            'title': 'important tasks',
            'sort': [
                ('stop', 'termin'),
                ('name', 'name'),
                ('created', 'create date'),
                ('in_my_day', 'my day'),
            ],
        },
        'planned': {
            'icon': 'check2-square',
            'title': 'planned tasks',
            'use_sub_groups': True,
            'sort': [
                ('stop', 'termin'),
                ('name', 'name'),
                ('created', 'create date'),
                ('important', 'important'),
                ('in_my_day', 'my day'),
            ],
        },
        'all': {
            'icon': 'infinity',
            'title': 'all tasks',
            'use_sub_groups': True,
            'hide_qty': True,
            'sort': [
                ('stop', 'termin'),
                ('name', 'name'),
                ('created', 'create date'),
                ('important', 'important'),
                ('in_my_day', 'my day'),
            ],
      },
        'completed': {
            'icon': 'check2-circle',
            'title': 'completed tasks',
            'hide_qty': True,
            'sort': [
                ('completion', 'completion date'),
                ('name', 'name'),
                ('created', 'create date'),
                ('important', 'important'),
            ],
        },
    }
}