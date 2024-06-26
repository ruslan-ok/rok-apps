from django.apps import AppConfig
from django.utils.translation import gettext, gettext_lazy as _

from task.const import APP_FAMILY


class FamilyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = APP_FAMILY
    app_config = {
        'name': APP_FAMILY,
        'app_title': _('family tree'),
        'human_name': gettext('Family tree'),
        'icon': 'diagram-3',
        'href': '/family/',
        'permission': 'task.view_pedigree',
        'order': 13,
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
