from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_DOCS,
    'app_title': _('documents'),
    'icon': 'file-text',
    'main_view': 'root',
    'use_groups': True,
    'group_entity_loc': pgettext_lazy('create ...', 'folder'),
    'sort': [
        ('name', _('name')),
    ],
    'views': {
        'root': {
            'role': ROLE_DOC,
            'role_loc': pgettext_lazy('add ... ', 'document'),
            'icon': 'file-text', 
            'title': _('Documents'),
        },
    }
}

