from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_PHOTO,
    'app_title': _('photo bank'),
    'icon': 'image',
    'main_view': 'preview',
    'use_groups': True,
    'group_entity_loc': pgettext_lazy('create ...', 'folder'),
    'role': ROLE_PHOTO,
    'sort': [
        ('name', _('name')),
    ],
    'views': {
        'preview': {
            'icon': 'images', 
            'title': _('photo preview'),
        },
        'map': {
            'icon': 'geo-alt', 
            'title': _('on the map'),
        },
    }
}

