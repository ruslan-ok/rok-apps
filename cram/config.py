from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

app_config = {
    'name': APP_CRAM,
    'role': ROLE_CRAM,
    'app_title': _('cram'),
    'icon': 'card-list',
    'main_view': 'index',
    'use_groups': True,
    'sort': [
        ('name', _('name')),
    ],
    'views': {
        'index': {
            'icon': 'translate',
            'title': _('Index'),
            'role': ROLE_CRAM,
        },
        # 'languages': {
        #     'icon': 'translate',
        #     'title': _('Languages'),
        #     'item_name': _('language'),
        #     'role': ROLE_LANG,
        # },
        # 'phrases': {
        #     'icon': 'heart',
        #     'title': _('Prases'),
        #     'role': ROLE_PHRASE,
        # },
        # 'training': {
        #     'icon': 'card-list',
        #     'title': _('Training'),
        #     'hide_qty': True,
        # },
    }
}

