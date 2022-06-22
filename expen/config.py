from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_EXPEN,
    'app_title': _('expenses'),
    'icon': 'cash-coin',
    'role': ROLE_EXPENSE,
    'role_loc': pgettext_lazy('add ...', 'expense'),
    'main_view': 'all',
    'use_groups': True,
    'group_entity': 'project',
    'group_entity_loc': pgettext_lazy('create ...', 'project'),
    'event_in_name': True,
    'sort': [
        ('event', _('operation date')),
        ('name', _('name')),
    ],
    'views': {
        'all': {
            'icon': 'infinity', 
            'title': _('all expenses'),
        },
    }
}

