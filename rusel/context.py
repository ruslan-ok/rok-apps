from django.utils.translation import gettext_lazy as _
#from rest_framework.renderers import JSONRenderer

from rusel.apps import get_app_human_name, get_apps_list, get_app_icon, get_app_by_role
from task.models import Group
#from task.serializers import TaskGrpSerializer

def get_base_context(request, role, detail, title):
    context = {}
    app = get_app_by_role(role)
    context['app'] = app
    context['app_human_name'] = get_app_human_name(app)
    context['content_icon'] = get_app_icon(app)
    context['role'] = role
    context['restriction'] = None
    cur_grp = get_cur_grp(request)
    title_1 = title_2 = url = ''
    if (not detail or not title) and cur_grp:
        title_1 = Group.objects.filter(id=cur_grp.id).get().name
    else:
        if title:
            if type(title) is tuple:
                if (len(title) > 0):
                    title_1 = title[0]
                if (len(title) > 1):
                    title_2 = title[1]
            else:
                title_1 = title
    context['list_id'] = 0
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
    
    context['complete_icon'] = 'icon/main/complete.svg'
    context['uncomplete_icon'] = 'icon/main/uncomplete.svg'
    
    context['apps'] = get_apps_list(request.user, app)

    #if url:
    #    save_last_visited(request.user, app + '/' + url, app, title_1, title_2)

    groups = []
    get_sorted_groups(groups, request.user.id, role)
    context['groups'] = groups
    if cur_grp:
        context['group_return'] = cur_grp.id
        if (not detail):
            context['group_path'] = get_group_path(cur_grp.id)

    context['add_item_placeholder'] = _('add task').capitalize()
    return context

def get_sorted_groups(groups, user_id, role, node=None):
    node_id = None
    if node:
        node_id = node.id
    items = Group.objects.filter(user=user_id, role=role, node=node_id).order_by('sort')
    for item in items:
        groups.append(item)
        get_sorted_groups(groups, user_id, role, item)
    
def get_cur_grp(request):
    cur_grp = None
    if request.method == 'GET':
        v = request.GET.get('view')
        if v and (v == 'by_group'):
            g = request.GET.get('group_id')
            if g:
                if Group.objects.filter(id=g, user=request.user.id).exists():
                    cur_grp = Group.objects.filter(id=g, user=request.user.id).get()
    return cur_grp

def get_group_path(cur_grp_id):
    ret = []
    if cur_grp_id:
        grp = Group.objects.filter(id=cur_grp_id).get()
        ret.append({'id': grp.id, 'name': grp.name, 'edit_url': grp.edit_url})
        parent = grp.node
        while parent:
            grp = Group.objects.filter(id=parent.id).get()
            ret.append({'id': grp.id, 'name': grp.name, 'edit_url': grp.edit_url})
            parent = grp.node
    return ret
