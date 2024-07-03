from django.apps import AppConfig
from django.utils.translation import gettext, pgettext_lazy, gettext_lazy as _

from task.const import APP_EXPEN, ROLE_EXPENSE, ROLE_TODO, ROLE_WARR

class ExpenConfig(AppConfig):
    name = APP_EXPEN
    app_config = {
        'name': APP_EXPEN,
        'app_title': _('expenses'),
        'human_name': gettext('Expenses'),
        'icon': 'piggy-bank',
        'permission': 'task.view_expense',
        'order': 6,
        'role': ROLE_EXPENSE,
        'role_loc': pgettext_lazy('add ...', 'expense'),
        'main_view': 'all',
        'use_groups': True,
        'group_entity': 'project',
        'group_entity_loc': pgettext_lazy('create ...', 'project'),
        'event_in_name': True,
        'relate': [ROLE_TODO, ROLE_WARR],
        'sort': [
            ('event', _('operation date')),
            ('name', _('name')),
        ],
        'views': {
            'all': {
                'icon': 'infinity', 
                'title': _('All expenses'),
            },
        }
    }

