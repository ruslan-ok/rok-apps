from django.apps import apps as django_apps
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from task.const import *

def get_apps_list(user, current):
    apps = []
    for app, config in django_apps.app_configs.items():
        if not hasattr(config, "app_config"):
            continue
        if (app == 'account') and not user.is_superuser:
            continue
        icon = config.app_config['icon']
        href = config.app_config['href']
        perm = config.app_config['permission']
        order = config.app_config['order']
        name = config.app_config['human_name']
        if perm and not user.has_perm(perm):
            continue
        apps.append({'icon': icon, 'href': href, 'name': name, 'active': current==app, 'order': order})
    return sorted(apps, key=lambda a: a['order'])

def get_related_roles(task, config):
    related_roles = []
    possible_related = []
    for role in config.relate:
        possible_related.append({'name': role, 'icon': ROLE_ICON[role], 'href': get_role_href(role, task.id)})
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
