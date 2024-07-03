from django.apps import AppConfig
from django.utils.translation import gettext, pgettext_lazy, gettext_lazy as _

from task.const import APP_TODO, ROLE_TODO, ROLE_NOTE, ROLE_NEWS, ROLE_EXPENSE

class TodoConfig(AppConfig):
    name = APP_TODO
    app_config = {
        'name': APP_TODO,
        'app_title': _('tasks'),
        'human_name': gettext('Tasks'),
        'icon': 'check2-square',
        'permission': 'task.view_todo',
        'order': 2,
        'role': ROLE_TODO,
        'role_loc': pgettext_lazy('add ... ', 'todo'),
        'main_view': 'planned',
        'use_groups': True,
        'use_selector': True,
        'use_important': True,
        'relate': [ROLE_NOTE, ROLE_NEWS, ROLE_EXPENSE],
        'sort': [
            ('stop', _('termin')),
            ('name', _('name')),
            ('created', _('create date')),
            ('completion', _('completion date')),
            ('important', _('important')),
            ('in_my_day', _('my day')),
        ],
        'views': {
            'myday': {
                'icon': 'sun',
                'title': _('My day'),
                'sort': [
                    ('stop', _('termin')),
                    ('name', _('name')),
                    ('created', _('create date')),
                    ('important', _('important')),
                ],
            },
            'important': {
                'icon': 'star',
                'title': _('Important tasks'),
                'sort': [
                    ('stop', _('termin')),
                    ('name', _('name')),
                    ('created', _('create date')),
                    ('in_my_day', _('my day')),
                ],
            },
            'planned': {
                'icon': 'check2-square',
                'title': _('Planned tasks'),
                'use_sub_groups': True,
                'hide_qty': True,
                'sort': [
                    ('stop', _('termin')),
                    ('name', _('name')),
                    ('created', _('create date')),
                    ('important', _('important')),
                    ('in_my_day', _('my day')),
                ],
            },
            'all': {
                'icon': 'infinity',
                'title': _('All tasks'),
                'use_sub_groups': True,
                'hide_qty': True,
                'sort': [
                    ('stop', _('termin')),
                    ('name', _('name')),
                    ('created', _('create date')),
                    ('important', _('important')),
                    ('in_my_day', _('my day')),
                ],
            },
            'completed': {
                'icon': 'check2-circle',
                'title': _('Completed tasks'),
                'hide_qty': True,
                'sort': [
                    ('completion', _('completion date')),
                    ('name', _('name')),
                    ('created', _('create date')),
                    ('important', _('important')),
                ],
            },
        }
    }
