from task.const import *

app_config = {
    'name': APP_ALL,
    'app_title': 'search results',
    'icon': 'search',
    'role': ROLE_SEARCH_RESULTS,
    'sort': [
        ('name', 'name'),
        ('created', 'create date'),
    ],
    'views': {
        'search': {
            'icon': 'search',
            'title': 'search results',
        },
    }
}