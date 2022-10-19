from django.utils.translation import gettext_lazy as _, pgettext_lazy
from task.const import *

LOCALIZED_INCIDENT = _('incident')

app_config = {
    'name': APP_HEALTH,
    'app_title': _('health'),
    'icon': 'star',
    'main_view': 'biomarker',
    'views': {
        'biomarker': {
            'role': ROLE_MARKER,
            'role_loc': pgettext_lazy('add ...', 'marker'),
            'icon': 'heart', 
            'title': _('biomarkers'),
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
            'title': _('incidents'),
            'sort': [
                ('name', _('name')),
                ('start', _('period')),
            ],
            'hide_qty': True,
        },
        'weight': {
            'role': ROLE_CHART_WEIGHT,
            'icon': 'graph-up', 
            'title': _('weight chart'),
            'hide_qty': True,
        },
        'waist': {
            'role': ROLE_CHART_WAIST,
            'icon': 'graph-up', 
            'title': _('waist chart'),
            'hide_qty': True,
        },
        'temp': {
            'role': ROLE_CHART_TEMP,
            'icon': 'graph-up', 
            'title': _('temperature chart'),
            'hide_qty': True,
        },
    }
}

