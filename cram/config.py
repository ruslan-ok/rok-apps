from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_CRAM,
    'app_title': _('cram'),
    'icon': 'card-list',
    'main_view': 'training',
    'use_groups': True,
    'sort': [
        ('name', _('name')),
    ],
    'views': {
        'languages': {
            'icon': 'translate',
            'title': _('Languages'),
            'item_name': _('language'),
            'role': ROLE_LANG,
        },
        'prases': {
            'icon': 'heart',
            'title': _('Prases'),
            'role': ROLE_PHRASE,
        },
        'training': {
            'icon': 'card-list',
            'title': _('Training'),
            'hide_qty': True,
        },
    }
}

