from django.utils.translation import gettext_lazy as _
from task.models import TaskGrp, AAppParam

APPS = {
    'home':    ('home',        '/'),
    'todo':    ('application', '/todo/'),
    'note':    ('note',        '/note/'),
    'news':    ('news',        '/news/'),
    'store':   ('key',         '/store/'),
    'proj':    ('cost',        '/proj/'),
    'trip':    ('car',         '/trip/'),
    'fuel':    ('gas',         '/fuel/'),
    'apart':   ('apartment',   '/apart/'),
    'wage':    ('work',        '/wage/'),
    'photo':   ('photo',       '/photo/'),
    'health':  ('health',      '/health/'),
    'admin':   ('admin',       '/admin/'),
    'profile': ('user',        '/account/profile/'),
    'logout':  ('exit',        '/account/logout/'),
}

def get_app_name(app):
    if (app == 'rusel'):
        return 'rusel.by'
    if (app == 'apart'):
        return 'communal'
    if (app == 'fuel'):
        return 'fuelings'
    if (app == 'note'):
        return 'notes'
    if (app == 'news'):
        return 'news'
    if (app == 'proj'):
        return 'expenses'
    if (app == 'store'):
        return 'passwords'
    if (app == 'todo'):
        return 'tasks'
    if (app == 'trip'):
        return 'trips'
    if (app == 'wage'):
        return 'work'
    if (app == 'photo'):
        return 'photobank'
    if (app == 'health'):
        return 'health'
    return None

def get_apps_list(user):
    beta = get_beta(user)
    apps = []
    for app in APPS:
        if (app in ('store', 'trip', 'apart', 'wage', 'health')) and (user.username != 'ruslan.ok'):
            continue
        if (app == 'admin') and (user.username != 'admin'):
            continue
        if (app == 'profile') and (user.username == 'demouser'):
            continue
        href = APPS[app][1]
        if beta and (app != 'home'):
            href = 'drf' + APPS[app][1]
        apps.append({'href': href, 'icon': 'rok/icon/' + APPS[app][0] + '.png', 'name': get_main_menu_item(app)})
    return apps

def get_app_params(user, app):
    if not AAppParam.objects.filter(user=user.id, app=app).exists():
        return AAppParam.objects.create(user=user, app=app, view=None, lst = None)
    return AAppParam.objects.filter(user=user.id, app=app).get()

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

def switch_beta(user):
    param = get_app_params(user, 'home')
    param.beta = not param.beta
    param.save()

def get_beta(user):
    param = get_app_params(user, 'home')
    return param.beta




