from django.utils.translation import gettext_lazy as _
from task.const import *

app_config = {
    'name': APP_PHOTO,
    'app_title': _('photo bank'),
    'icon': 'image',
    'main_view': 'preview',
    'use_groups': True,
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

