from django.apps import AppConfig
from django.utils.translation import gettext, pgettext_lazy, gettext_lazy as _

class PhotoConfig(AppConfig):
    name = 'photo'
    app_config = {
        'name': 'photo',
        'app_title': _('photo bank'),
        'human_name': gettext('Photobank'),
        'icon': 'image',
        'permission': 'photo.view_photo',
        'order': 12,
        'main_view': 'preview',
        'use_groups': True,
        'group_entity_loc': pgettext_lazy('create ...', 'folder'),
        'role': 'photo',
        'sort': [
            ('name', _('name')),
        ],
        'views': {
            'preview': {
                'icon': 'images', 
                'title': _('Photo preview'),
            },
            'map': {
                'icon': 'geo-alt', 
                'title': _('On the map'),
            },
        }
    }
