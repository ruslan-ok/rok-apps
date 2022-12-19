from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_FAMILY,
    'app_title': _('family tree'),
    'icon': 'diagram-3',
    'main_view': 'pedigree',
    'group_entity': 'tree',
    'views': {
        'pedigree': {
            'title': _('Pedigree'),
            'icon': 'collection', 
            'use_important': True,
        },
        'diagram': {
            'title': _('Diagram'),
            'icon': 'diagram-3', 
            'hide_qty': True,
            'role': 'diagram',
        },
    }
}

