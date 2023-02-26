from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_FUEL,
    'app_title': _('fueling'),
    'icon': 'fuel-pump',
    'main_view': 'fuel',
    'group_entity': 'car',
    'group_entity_loc': pgettext_lazy('create ...', 'car'),
    'views': {
        'fuel': {
            'role': ROLE_FUEL,
            'role_loc': pgettext_lazy('add ... ', 'fueling'),
            'icon': 'fuel-pump',
            'title': _('Fuelings'),
            'add_button': True,
            'hide_qty': True,
            'sort': [
                ('event', _('fueling date')),
            ],
        },
        'part': {
            'role': ROLE_PART,
            'icon': 'cart', 
            'title': _('Itnervals'),
            'item_name': _('service interval'),
            'hide_qty': True,
        },
        'service': {
            'role': ROLE_SERVICE,
            'icon': 'tools', 
            'title': _('Services'),
            'item_name': _('service'),
            'add_button': True,
            'use_sub_groups': True,
            'relate': [ROLE_EXPENSE],
            'hide_qty': True,
            'sort': [
                ('event', _('due date')),
            ],
        },
        'car': {
            'role': ROLE_CAR,
            'icon': 'truck', 
            'title': _('Cars'),
            'item_name': _('car'),
            'hide_qty': True,
            'sort': [
                ('name', _('name')),
                ('start', _('date of commencement')),
            ],
        },
        'map': {
            'icon': 'geo-alt', 
            'title': _('On the map'),
            'hide_qty': True,
        },
    }
}

