from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_TODO,
    'app_title': _('tasks'),
    'icon': 'check2-square',
    'role': ROLE_TODO,
    'role_loc': pgettext_lazy('add ... ', 'todo'),
    'main_view': 'planned',
    'use_groups': True,
    'use_selector': True,
    'use_important': True,
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
            'title': _('my day'),
            'sort': [
                ('stop', _('termin')),
                ('name', _('name')),
                ('created', _('create date')),
                ('important', _('important')),
            ],
        },
        'important': {
            'icon': 'star',
            'title': _('important tasks'),
            'sort': [
                ('stop', _('termin')),
                ('name', _('name')),
                ('created', _('create date')),
                ('in_my_day', _('my day')),
            ],
        },
        'planned': {
            'icon': 'check2-square',
            'title': _('planned tasks'),
            'use_sub_groups': True,
            'sort': [
                ('stop', _('termin')),
                ('name', _('name')),
                ('created', _('create date')),
                ('important', _('important')),
                ('in_my_day', _('my day')),
            ],
            'relate': [ROLE_NOTE, ROLE_NEWS],
        },
        'all': {
            'icon': 'infinity',
            'title': _('all tasks'),
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
            'title': _('completed tasks'),
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