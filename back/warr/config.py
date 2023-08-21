from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_WARR,
    'app_title': _('warranties'),
    'icon': 'award',
    'main_view': 'active',
    'use_groups': True,
    'role': ROLE_WARR,
    'role_loc': pgettext_lazy('add ...', 'warranty'),
    'relate': [ROLE_EXPENSE],
    'sort': [
        ('stop', _('termin')),
        ('name', _('name')),
    ],
    'views': {
        'active': {
            'icon': 'award', 
            'title': _('Active warranties'),
        },
        'expired': {
            'icon': 'award', 
            'title': _('Expired warranties'),
        },
        'all': {
            'icon': 'award', 
            'title': _('All warranties'),
        },
    }
}

