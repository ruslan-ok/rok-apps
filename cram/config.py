from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_CRAM,
    'app_title': _('cram'),
    'icon': 'card-list',
    'role': ROLE_CRAM,
    'main_view': 'prases',
    'use_groups': True,
    'sort': [
        ('name', _('name')),
    ],
    'views': {
        'prases': {
            'icon': 'heart',
            'title': _('Prases'),
        },
        'training': {
            'icon': 'card-list',
            'title': _('Training'),
            'hide_qty': True,
        },
    }
}

