from task.const import *

app_config = {
    'name': APP_NOTE,
    'app_title': 'notes',
    'icon': 'sticky',
    'role': ROLE_NOTE,
    'groups': True,
    'views': {
        'note': {
            'icon': 'check-all',
            'title': 'all',
        },
    }
}
