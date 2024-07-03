from django.apps import AppConfig
from django.utils.translation import gettext, pgettext_lazy, gettext_lazy as _

from task.const import APP_NOTE, ROLE_NOTE, ROLE_TODO, ROLE_NEWS

class NoteConfig(AppConfig):
    name = APP_NOTE
    app_config = {
        'name': APP_NOTE,
        'app_title': _('notes'),
        'human_name': gettext('Notes'),
        'icon': 'sticky',
        'permission': 'task.view_note',
        'order': 3,
        'role': ROLE_NOTE,
        'role_loc': pgettext_lazy('add ... ', 'note'),
        'main_view': 'all',
        'use_groups': True,
        'relate': [ROLE_TODO, ROLE_NEWS],
        'sort': [
            ('event', _('event date')),
            ('name', _('name')),
        ],
        'views': {
            'all': {
                'icon': 'infinity',
                'title': _('All'),
            },
        }
    }
