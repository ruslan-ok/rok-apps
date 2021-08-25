from django.utils.translation import gettext_lazy as _
#from rest_framework.renderers import JSONRenderer

from rusel.apps import get_app_name, get_apps_list
from task.models import Group
#from task.serializers import TaskGrpSerializer

def get_base_context(request, app, detail, title):
    context = {}
    context['app'] = app
    context['app_name'] = get_app_name(app)
    context['restriction'] = None
    title_1 = title_2 = url = ''
    if title:
        if type(title) is tuple:
            if (len(title) > 0):
                title_1 = title[0]
            if (len(title) > 1):
                title_2 = title[1]
        else:
            title_1 = title
    context['article_visible'] = detail
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
    get_sorted_groups(groups, request.user.id, app)
    context['groups'] = groups

    context['add_item_placeholder'] = _('add task').capitalize()
    return context

def get_sorted_groups(groups, user_id, app, node=None):
    node_id = None
    if node:
        node_id = node.id
    items = Group.objects.filter(user=user_id, app=app, node=node_id).order_by('sort')
    for item in items:
        groups.append(item)
        get_sorted_groups(groups, user_id, app, item)
    
