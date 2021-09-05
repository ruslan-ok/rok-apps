from django.utils.translation import gettext_lazy as _
from task.models import Task
from task.const import *

APPS = {
    'home':    ('house-door',        '/'),
    'todo':    ('check2-square',        '/todo/'),
    'note':    ('sticky',        '/note/'),
    'news':    ('newspaper',        '/news/'),
    'store':   ('key',       '/store/'),
    'proj':    ('piggy-bank',        '/proj/'),
    'trip':    ('truck',        '/trip/'),
    'fuel':    ('droplet',        '/fuel/'),
    'apart':   ('building',       '/apart/'),
    'wage':    ('briefcase',        '/wage/'),
    'photo':   ('image',       '/photo/'),
    'health':  ('heart',      '/health/'),
    'admin':   ('people',       '/admin/'),
    'profile': ('person',  '/account/profile/'),
    'logout':  ('box-arrow-right',   '/account/logout/'),
}

def _get_app_human_name(app):
    if (app == 'home'):
        return 'rusel.by'
    if (app == 'apart'):
        return _('communal')
    if (app == 'fuel'):
        return _('fuelings')
    if (app == 'note'):
        return _('notes')
    if (app == 'news'):
        return _('news')
    if (app == 'proj'):
        return _('expenses')
    if (app == 'store'):
        return _('passwords')
    if (app == 'todo'):
        return _('tasks').capitalize()
    if (app == 'trip'):
        return _('trips')
    if (app == 'wage'):
        return _('work')
    if (app == 'photo'):
        return _('photobank')
    if (app == 'health'):
        return _('health')
    return None

def get_app_human_name(role):
    app = get_app_by_role(role)
    name = _get_app_human_name(app)
    if (app == 'home'):
        return name
    if name:
        return _(name).capitalize()
    return None

def get_apps_list(user, current):
    apps = []
    for app in APPS:
        if (app in ('store', 'trip', 'apart', 'wage', 'health')) and (user.username != 'ruslan.ok'):
            continue
        if (app == 'admin') and (user.username != 'admin'):
            continue
        if (app == 'profile') and (user.username == 'demouser'):
            continue
        if (app == 'profile') or (app == 'logout'):
            continue
        href = APPS[app][1]
        apps.append({'href': href, 'icon': APPS[app][0], 'name': get_main_menu_item(app), 'active': current==app})
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
    if (app == 'profile'):
        return _('profile').capitalize()
    if (app == 'logout'):
        return _('log out').capitalize()
    return None
