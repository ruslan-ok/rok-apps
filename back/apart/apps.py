from django.apps import AppConfig
from django.utils.translation import gettext, pgettext_lazy, gettext_lazy as _

from task.const import APP_APART, ROLE_BILL, ROLE_TODO, ROLE_METER, ROLE_PRICE, ROLE_APART


class ApartConfig(AppConfig):
    name = 'apart'
    verbose_name = _('apart')
    app_config = {
        'name': APP_APART,
        'app_title': _('communal'),
        'human_name': gettext('Communal'),
        'icon': 'building',
        'href': '/bill/',
        'permission': 'task.view_apart',
        'order': 8,
        'main_view': 'bill',
        'group_entity': 'apart',
        'group_entity_loc': pgettext_lazy('create ...', 'apart'),
        'views': {
            'bill': {
                'role': ROLE_BILL,
                'role_loc': pgettext_lazy('add ... ', 'bill'),
                'icon': 'receipt', 
                'title': _('Bills'),
                'add_button': True,
                'relate': [ROLE_TODO],
                'sort': [
                    ('name', _('name')),
                    ('start', _('period')),
                ],
            },
            'meter': {
                'role': ROLE_METER,
                'role_loc': pgettext_lazy('add ... ', 'meter'),
                'icon': 'speedometer2', 
                'title': _('Meters data'),
                'item_name': _('meters data'),
                'add_button': True,
                'relate': [ROLE_TODO],
                'sort': [
                    ('name', _('name')),
                    ('start', _('period')),
                ],
            },
            'price': {
                'role': ROLE_PRICE,
                'role_loc': pgettext_lazy('add ... ', 'price'),
                'icon': 'tag', 
                'title': _('Prices'),
                'add_button': True,
                'use_sub_groups': True,
                'sort': [
                    ('name', _('name')),
                    ('start', _('valid from')),
                ],
            },
            'apart': {
                'role': ROLE_APART,
                'role_loc': pgettext_lazy('add ... ', 'apart'),
                'icon': 'building', 
                'title': _('Apartments'),
                'item_name': _('apartment'),
                'sort': [
                    ('name', _('name')),
                    ('sort', _('sort code')),
                ],
            },
        }
    }
