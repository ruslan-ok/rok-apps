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
            'icon': 'fuel-pump',
            'title': _('fuelings'),
            'item_name': _('fueling'),
            'add_button': True,
            'sort': [
                ('event', _('fueling date')),
            ],
        },
        'part': {
            'role': ROLE_PART,
            'icon': 'cart', 
            'title': _('itnervals'),
            'item_name': _('service interval'),
        },
        'service': {
            'role': ROLE_SERVICE,
            'icon': 'tools', 
            'title': _('services'),
            'item_name': _('service'),
            'add_button': True,
            'use_sub_groups': True,
            'relate': [ROLE_EXPENSE],
            'sort': [
                ('event', _('due date')),
            ],
        },
        'car': {
            'role': ROLE_CAR,
            'icon': 'truck', 
            'title': _('cars'),
            'item_name': _('car'),
            'sort': [
                ('name', _('name')),
                ('start', _('date of commencement')),
            ],
        },
    }
}

