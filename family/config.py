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
        'individual': {
            'title': _('Individuals'),
            'icon': 'person', 
            'role': 'individual',
        },
        'family': {
            'title': _('Families'),
            'icon': 'people', 
            'role': 'family',
        },
        'media': {
            'title': _('Media'),
            'icon': 'image', 
            'role': 'media',
        },
        'repo': {
            'title': _('Repository'),
            'icon': 'file-text', 
            'role': 'repo',
        },
        'note': {
            'title': _('Notes'),
            'icon': 'stickies', 
            'role': 'note',
        },
        'source': {
            'title': _('Sources'),
            'icon': 'stickies', 
            'role': 'source',
        },
        'submitter': {
            'title': _('Submitters'),
            'icon': 'stickies', 
            'role': 'submitter',
        },
        'report': {
            'title': _('Reports'),
            'icon': 'file-text', 
            'role': 'report',
            'hide_qty': True,
        },
        'calendar': {
            'title': _('Calendar'),
            'icon': 'calendar3', 
            'role': 'calendar',
            'hide_qty': True,
        },
    }
}

