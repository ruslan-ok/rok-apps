from django.apps import AppConfig
from django.utils.translation import gettext, pgettext_lazy, gettext_lazy as _

from task.const import APP_STORE, ROLE_STORE

class StoreConfig(AppConfig):
    name = APP_STORE
    app_config = {
        'name': APP_STORE,
        'app_title': _('passwords'),
        'human_name': gettext('Passwords'),
        'icon': 'key',
        'href': '/store/',
        'permission': 'task.view_entry',
        'order': 5,
        'role': ROLE_STORE,
        'role_loc': pgettext_lazy('add ... ', 'password'),
        'main_view': 'actual',
        'use_groups': True,
        'use_selector': True,
        'sort': [
            ('name', _('name')),
            ('created', _('create date')),
        ],
        'views': {
            'actual': {
                'icon': 'key',
                'title': _('Actual'),
            },
            'completed': {
                'icon': 'check2-circle',
                'title': _('Unactual'),
            },
            'all': {
                'icon': 'infinity',
                'title': _('All'),
                'use_sub_groups': True,
                # 'hide_qty': True,
            },
            'params': {
                'page_url': 'params',
                'icon': 'gear', 
                'title': _('Default parameters'),
                'hide_qty': True,
            },
        }
    }
