from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_FAMILY,
    'app_title': _('family tree'),
    'icon': 'diagram-3',
    'main_view': 'tree',
    'group_entity': 'tree',
    'views': {
        'pedigree': {
            'title': _('Pedigree'),
            'icon': 'collection', 
            'role': 'pedigree',
            'use_important': True,
        },
        'tree': {
            'title': _('Diagram'),
            'icon': 'diagram-3', 
            'hide_qty': True,
        },
        'calendar': {
            'title': _('Calendar'),
            'icon': 'calendar3', 
            'role': 'calendar',
            'hide_qty': True,
        },
        'people': {
            'title': _('Individuals'),
            'icon': 'person', 
            'role': 'individual',
        },
        'families': {
            'title': _('Families'),
            'icon': 'people', 
            'role': 'family',
        },
        'notes': {
            'title': _('Notes'),
            'icon': 'stickies', 
            'role': 'notes',
            'hide_qty': True,
        },
        'media': {
            'title': _('Media'),
            'icon': 'image', 
            'role': 'media',
        },
        'reports': {
            'title': _('Reports'),
            'icon': 'file-text', 
            'role': 'reports',
            'hide_qty': True,
        },
    }
}

