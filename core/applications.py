from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from task import const
from task.const import *

APPS = {
    APP_HOME:    ('house-door',    '/',         ''),
    APP_TODO:    ('check2-square', '/todo/',    'task.view_todo'),
    APP_NOTE:    ('sticky',        '/note/',    'task.view_note'),
    APP_NEWS:    ('newspaper',     '/news/',    'task.view_news'),
    APP_STORE:   ('key',           '/store/',   'task.view_entry'),
    APP_EXPEN:   ('piggy-bank',    '/expen/',   'task.view_expense'),
    APP_FUEL:    ('fuel-pump',     '/fuel/',    'task.view_fuel'),
    APP_APART:   ('building',      '/bill/',    'task.view_apart'),
    APP_HEALTH:  ('heart',         '/health/',  'task.view_health'),
    APP_DOCS:    ('file-text',     '/docs/',    'task.view_docs'),
    APP_WARR:    ('award',         '/warr/',    'task.view_warranty'),
    APP_PHOTO:   ('image',         '/photo/',   'task.view_photo'),
    APP_FAMILY:  ('diagram-3',     '/family/',  'family.view_pedigree'),
    APP_LOGS:    ('card-list',     '/logs/',    'task.view_logs'),
    APP_ADMIN:   ('people',        '/admin/',   'task.administrate_site'),
}

def _get_app_human_name(app):
    match app:
        case const.APP_HOME: ret = 'rusel.by'
        case const.APP_TODO: ret = _('tasks')
        case const.APP_NOTE: ret = _('notes')
        case const.APP_NEWS: ret = _('news')
        case const.APP_STORE: ret = _('passwords')
        case const.APP_DOCS: ret = _('documents')
        case const.APP_WARR: ret = _('warranties')
        case const.APP_EXPEN: ret = _('expenses')
        case const.APP_TRIP: ret = _('trips')
        case const.APP_FUEL: ret = _('fuelings')
        case const.APP_APART: ret = _('communal')
        case const.APP_WORK: ret = _('work')
        case const.APP_PHOTO: ret = _('photobank')
        case const.APP_FAMILY: ret = _('family tree')
        case const.APP_HEALTH: ret = _('health')
        case const.APP_ADMIN: ret = _('administrative tools')
        case const.APP_LOGS: ret = _('logs')
        case const.APP_CRAM: ret = _('cram')
        case _: ret = None
    return ret

def get_app_human_name(app):
    name = _get_app_human_name(app)
    if (app == APP_HOME):
        return name
    if name:
        return _(name).capitalize()
    return None

def get_apps_list(user, current):
    apps = []
    for app in APPS:
        icon = APPS[app][0]
        href = APPS[app][1]
        perm = APPS[app][2]
        if perm and not user.has_perm(perm):
            continue
        if perm and user.is_superuser and app != APP_ADMIN:
            continue
        apps.append({'icon': icon, 'href': href, 'name': get_main_menu_item(app), 'active': current==app})
    return apps

def get_main_menu_item(app):
    name = get_app_human_name(app)
    if name and (app != 'home'):
        return name
    if (app == APP_HOME):
        return _('home').capitalize()
    if (app == APP_NEWS):
        return _('news').capitalize()
    if (app == APP_ADMIN):
        return _('admin').capitalize()
    return None

def get_app_icon(app):
    return APPS[app][0]

def get_related_roles(task, config):
    related_roles = []
    possible_related = []
    for role in config.relate:
        possible_related.append({'name': role, 'icon': ROLE_ICON[role], 'href': get_role_href(role, task.id)})
    for app_role in (task.app_task, task.app_note, task.app_news, task.app_store, #task.app_doc, 
                    task.app_expen, task.app_apart, task.app_fuel, task.app_warr#, task.app_trip, 
                    #task.app_health, task.app_work, task.app_photo
                    ):
        check_role(related_roles, possible_related, app_role, config, task.id)
    return related_roles, possible_related

def check_role(related_roles, possible_related, num_role, config, task_id):
    if num_role and (num_role != NONE):
        role = ROLE_BY_NUM[num_role]
        if (role != config.get_cur_role()):
            related_role = {'name': role}
            related_role['icon'] = ROLE_ICON[role]
            related_role['href'] = get_role_href(role, task_id)
            if (related_role in possible_related):
                possible_related.remove(related_role)
            related_roles.append(related_role)

def get_role_href(role, task_id):
    app = ROLE_APP[role]
    if role in ROLE_BASE:
        return reverse(app + ':' + role + '-item', args=[task_id])
    return reverse(app + ':' + 'item', args=[task_id])
