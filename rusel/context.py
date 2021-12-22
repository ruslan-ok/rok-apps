from datetime import datetime
from django.utils.translation import gettext_lazy as _
from rusel.apps import get_apps_list
from task.models import Group, VisitedHistory
from task.const import APP_HOME, APP_NAME

MAX_LAST_VISITED = 10

def get_base_context(request, app, role, group, detail, title, icon=None):
    context = {}
    if icon:
        context['icon'] = icon
    if hasattr(request.user, 'userext') and request.user.userext.avatar_mini:
        context['avatar'] = request.user.userext.avatar_mini.url
    else:
        context['avatar'] = '/static/Default-avatar.jpg'

    title_1 = title_2 = ''
    if (not detail or not title) and group and (group.determinator != 'role') and (group.determinator != 'view'):
        title_1 = Group.objects.filter(id=group.id).get().name
    else:
        if title:
            if type(title) is tuple:
                if (len(title) > 0):
                    title_1 = title[0]
                if (len(title) > 1):
                    title_2 = title[1]
            else:
                title_1 = title
    if not title_1 and not title_2:
        context['title'] = ''
    if title_1 and not title_2:
        context['title'] = title_1
    if not title_1 and title_2:
        context['title'] = title_2
    if title_1 and title_2:
        context['title'] = '{} [{}]'.format(_(title_1), title_2)

    context['please_correct_one'] = _('Please correct the error below.')
    context['please_correct_all'] = _('Please correct the errors below.')
    context['delete_question'] = _('delete').capitalize()
    
    context['complete_icon'] = 'icon/main/complete.svg'
    context['uncomplete_icon'] = 'icon/main/uncomplete.svg'
    
    context['apps'] = get_apps_list(request.user, app)

    if (request.method == 'GET'):
        url = request.path
        if (len(request.GET) > 0):
            url += '?'
            first = True
            for k in request.GET:
                if first:
                    first = False
                else:
                    url += '&'
                url += k + '=' + request.GET[k]
        save_last_visited(request.user, url, app, title_1, title_2, icon)

    groups = []
    get_sorted_groups(groups, request.user.id, role)
    context['groups'] = groups
    context['theme_id'] = 8
    if group:
        context['group_return'] = group.id
        if (not detail):
            if (not group.determinator) or (group.determinator == 'group'):
                context['group_path'] = get_group_path(group.id)
            if group.theme:
                context['theme_id'] = group.theme

    return context

def get_sorted_groups(groups, user_id, role, node=None):
    node_id = None
    if node:
        node_id = node.id
    items = Group.objects.filter(user=user_id, role=role, node=node_id).order_by('sort')
    for item in items:
        if (item.determinator != 'role') and (item.determinator != 'view'):
            groups.append(item)
            get_sorted_groups(groups, user_id, role, item)


def get_group_path(cur_grp_id):
    ret = []
    if cur_grp_id:
        grp = Group.objects.filter(id=cur_grp_id).get()
        ret.append({'id': grp.id, 'name': grp.name, 'edit_url': grp.edit_url()})
        parent = grp.node
        while parent:
            grp = Group.objects.filter(id=parent.id).get()
            ret.append({'id': grp.id, 'name': grp.name, 'edit_url': grp.edit_url()})
            parent = grp.node
    return ret

def save_last_visited(user, url, app, title_1, title_2, icon):
    if not title_1 and not title_2:
        return

    if (app == APP_HOME):
        return
    
    str_app = APP_NAME[app]
    
    pages = VisitedHistory.objects.filter(user=user.id).order_by('stamp')
    
    for page in pages:
        if (page.url == url) and (page.app == str_app):
            page.stamp = datetime.now()
            page.page = title_1
            page.info = title_2
            page.icon = icon
            page.save()
            return

    if (len(pages) >= MAX_LAST_VISITED):
        pages[0].delete()

    VisitedHistory.objects.create(user=user, stamp=datetime.now(), url=url, app=str_app, page=title_1, info=title_2, icon=icon)
