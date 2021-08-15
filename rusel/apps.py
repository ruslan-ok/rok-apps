from django.utils.translation import gettext_lazy as _
from task.models import Task

APPS = {
    'home':    ('icon/bootstrap/house-door.svg',        '/'),
    'todo':    ('icon/bootstrap/calendar-check.svg',    '/todo/'),
    'note':    ('icon/bootstrap/sticky.svg',            '/note/'),
    'news':    ('icon/bootstrap/newspaper.svg',         '/news/'),
    'store':   ('icon/bootstrap/key.svg',               '/store/'),
    'proj':    ('icon/bootstrap/cash-coin.svg',         '/proj/'),
    'trip':    ('icon/bootstrap/truck.svg',             '/trip/'),
    'fuel':    ('icon/bootstrap/droplet.svg',           '/fuel/'),
    'apart':   ('icon/bootstrap/building.svg',          '/apart/'),
    'wage':    ('icon/bootstrap/briefcase.svg',         '/wage/'),
    'photo':   ('icon/bootstrap/image.svg',             '/photo/'),
    'health':  ('icon/bootstrap/heart.svg',             '/health/'),
    'admin':   ('icon/bootstrap/people.svg',            '/admin/'),
    'profile': ('icon/bootstrap/person.svg',            '/account/profile/'),
    'logout':  ('icon/bootstrap/box-arrow-right.svg',   '/account/logout/'),
}

def get_app_name(app):
    if (app == 'rusel'):
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

def _get_app_name(app):
    name = get_app_name(app)
    if name:
        return _(name).capitalize()
    return None

def get_main_menu_item(app):
    name = _get_app_name(app)
    if name:
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

