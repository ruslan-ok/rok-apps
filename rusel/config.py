from django.utils.translation import gettext_lazy as _
from task.const import *

app_config = {
    'name': APP_ALL,
    'app_title': _('search results'),
    'icon': 'search',
    'role': ROLE_SEARCH_RESULTS,
    'sort': [
        ('name', _('name')),
        ('created', _('create date')),
    ],
    'views': {
        'search': {
            'icon': 'search',
            'title': 'search results',
        },
    }
}