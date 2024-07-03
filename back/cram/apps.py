from django.apps import AppConfig
from django.utils.translation import gettext, pgettext_lazy, gettext_lazy as _

from task.const import APP_CRAM, ROLE_CRAM


class CramConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = APP_CRAM
    app_config = {
        'name': APP_CRAM,
        'app_title': _('cram'),
        'human_name': gettext('Cram'),
        'icon': 'translate',
        'permission': 'cram.view_phrase',
        'order': 14,
        'role': ROLE_CRAM,
    }
