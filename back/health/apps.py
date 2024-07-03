from django.apps import AppConfig
from django.utils.translation import gettext, pgettext_lazy, gettext_lazy as _

from task.const import APP_HEALTH, ROLE_MARKER, ROLE_INCIDENT, ROLE_CHART_WEIGHT, ROLE_CHART_WAIST, ROLE_CHART_TEMP

class HealthConfig(AppConfig):
    name = APP_HEALTH
    app_config = {
        'name': APP_HEALTH,
        'app_title': _('health'),
        'human_name': gettext('Health'),
        'icon': 'heart',
        'permission': 'task.view_health',
        'order': 9,
        'main_view': 'biomarker',
        'views': {
            'biomarker': {
                'role': ROLE_MARKER,
                'role_loc': pgettext_lazy('add ...', 'marker'),
                'icon': 'heart', 
                'title': _('Biomarkers'),
                'limit_list': 10,
                'sort': [
                    ('event', _('event date')),
                ],
                'hide_qty': True,
            },
            'incident': {
                'role': ROLE_INCIDENT,
                'role_loc': pgettext_lazy('add ...', 'incident'),
                'icon': 'thermometer-half', 
                'title': _('Incidents'),
                'sort': [
                    ('name', _('name')),
                    ('start', _('period')),
                ],
                'hide_qty': True,
            },
            'weight': {
                'role': ROLE_CHART_WEIGHT,
                'icon': 'graph-up', 
                'title': _('Weight chart'),
                'hide_qty': True,
            },
            'waist': {
                'role': ROLE_CHART_WAIST,
                'icon': 'graph-up', 
                'title': _('Waist chart'),
                'hide_qty': True,
            },
            'temp': {
                'role': ROLE_CHART_TEMP,
                'icon': 'graph-up', 
                'title': _('Temperature chart'),
                'hide_qty': True,
            },
        }
    }

