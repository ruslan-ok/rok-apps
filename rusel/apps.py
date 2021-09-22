from django.utils.translation import gettext_lazy as _
from task.const import *

APPS = {
    'home':    ('house-door',    '/'),
    'todo':    ('check2-square', '/todo/'),
    'note':    ('sticky',        '/note/'),
    'news':    ('newspaper',     '/news/'),
    'store':   ('key',           '/store/'),
    'expen':   ('piggy-bank',    '/expen/'),
    'trip':    ('truck',         '/trip/'),
    'fuel':    ('droplet',       '/fuel/'),
    'apart':   ('building',      '/apart/'),
    'work':    ('briefcase',     '/work/'),
    'health':  ('heart',         '/health/'),
    'docs':    ('file-text',     '/docs/'),
    'warr':    ('award',         '/warr/'),
    'photo':   ('image',         '/photo/'),
    'admin':   ('people',        '/admin/'),
}

def _get_app_human_name(app):
    if (app == 'home'):
        return 'rusel.by'
    if (app == 'todo'):
        return _('tasks')
    if (app == 'note'):
        return _('notes')
    if (app == 'news'):
        return _('news')
    if (app == 'store'):
        return _('passwords')
    if (app == 'docs'):
        return _('documents')
    if (app == 'warr'):
        return _('warranties')
    if (app == 'expen'):
        return _('expenses')
    if (app == 'trip'):
        return _('trips')
    if (app == 'fuel'):
        return _('fuelings')
    if (app == 'apart'):
        return _('communal')
    if (app == 'work'):
        return _('work')
    if (app == 'photo'):
        return _('photobank')
    if (app == 'health'):
        return _('health')
    if (app == 'admin'):
        return _('administrative tools')
    return None

def get_app_human_name(app):
    name = _get_app_human_name(app)
    if (app == 'home'):
        return name
    if name:
        return _(name).capitalize()
    return None

def get_apps_list(user, current):
    apps = []
    for app in APPS:
        if (app in ('store', 'trip', 'apart', 'work', 'health', 'warr')) and (user.username != 'ruslan.ok'):
            continue
        if (app == 'admin') and (user.username != 'admin'):
            continue
        apps.append({'icon': APPS[app][0], 'href': APPS[app][1], 'name': get_main_menu_item(app), 'active': current==app})
    return apps

def get_main_menu_item(app):
    name = get_app_human_name(app)
    if name and (app != 'home'):
        return name
    if (app == 'home'):
        return _('home').capitalize()
    if (app == 'news'):
        return _('news').capitalize()
    if (app == 'admin'):
        return _('admin').capitalize()
    return None

def get_app_icon(app):
    return APPS[app][0]