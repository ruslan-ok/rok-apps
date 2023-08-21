from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_FAMILY,
    'app_title': _('family tree'),
    'icon': 'diagram-3',
    'main_view': 'diagram',
    'group_entity': 'tree',
    'views': {
        'diagram': {
            'title': _('Diagram'),
            'icon': 'diagram-3', 
            'hide_qty': True,
        },
        'pedigree': {
            'title': _('Pedigree'),
            'icon': 'collection', 
            'use_important': True,
            'role': 'pedigree',
        },
        'person': {
            'title': _('Person'),
            'icon': 'person', 
            'hide_qty': True,
            'role': 'individual',
        },
    }
}

