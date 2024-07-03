from django.apps import AppConfig
from django.utils.translation import gettext, pgettext_lazy, gettext_lazy as _

class DocsConfig(AppConfig):
    name = 'docs'
    app_config = {
        'name': 'docs',
        'app_title': _('documents'),
        'human_name': gettext('Documents'),
        'icon': 'file-text',
        'permission': 'task.view_docs',
        'order': 10,
        'main_view': 'root',
        'use_groups': True,
        'group_entity_loc': pgettext_lazy('create ...', 'folder'),
        'sort': [
            ('name', _('name')),
        ],
        'views': {
            'root': {
                'role': 'doc',
                'role_loc': pgettext_lazy('add ... ', 'document'),
                'icon': 'file-text', 
                'title': _('Documents'),
            },
        }
    }
