from django.utils.translation import gettext_lazy as _
from task.const import *

app_config = {
    'name': APP_ALL,
    'app_title': _('home page'),
    'icon': 'house',
    'main_view': 'home',
    'use_selector': True,
    'use_important': True,
    'sort': [
        ('name', _('name')),
        ('created', _('create date')),
    ],
    'views': {
        'home': {
            'icon': 'house',
            'title': _('home page'),
            'use_sub_groups': True,
        },
    }
}