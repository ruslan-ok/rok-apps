from django.apps import AppConfig
from django.utils.translation import gettext, pgettext_lazy, gettext_lazy as _

class WarrConfig(AppConfig):
    name = 'warr'
    app_config = {
        'name': 'warr',
        'app_title': _('warranties'),
        'human_name': gettext('Warranties'),
        'icon': 'award',
        'href': '/warr/',
        'permission': 'task.view_warranty',
        'order': 11,
        'main_view': 'active',
        'use_groups': True,
        'role': 'warr',
        'role_loc': pgettext_lazy('add ...', 'warranty'),
        'relate': ['expense'],
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
