from django.apps import AppConfig
from django.utils.translation import gettext, pgettext_lazy, gettext_lazy as _

from task.const import APP_NEWS, ROLE_NEWS, ROLE_TODO, ROLE_NOTE

class NewsConfig(AppConfig):
    name = APP_NEWS
    app_config = {
        'name': APP_NEWS,
        'app_title': _('news'),
        'human_name': gettext('News'),
        'icon': 'newspaper',
        'permission': 'task.view_news',
        'order': 4,
        'role': ROLE_NEWS,
        'role_loc': pgettext_lazy('add ... ', 'news'),
        'main_view': 'all',
        'use_groups': True,
        'relate': [ROLE_TODO, ROLE_NOTE],
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
