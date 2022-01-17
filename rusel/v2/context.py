from django.utils.translation import gettext_lazy as _
#from rest_framework.renderers import JSONRenderer

from rusel.apps import get_app_name, get_beta, get_apps_list
from task.models import Group
#from task.serializers import TaskGrpSerializer

def get_base_context(request, app, detail, title):
    context = {}
    context['app'] = app
    context['app_name'] = get_app_name(app)
    context['restriction'] = None
    context['beta'] = get_beta(request.user)
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
    
    context['complete_icon'] = 'v2/todo/icon/complete.png'
    context['uncomplete_icon'] = 'v2/todo/icon/uncomplete.png'
    
    context['apps'] = get_apps_list(request.user)

    #if url:
    #    save_last_visited(request.user, app + '/' + url, app, title_1, title_2)

    groups = Group.objects.filter(user=request.user.id, app=app).order_by('sort')
    context['groups'] = groups #JSONRenderer().render(TaskGrpSerializer(groups, many=True, context={'request': request}).data)

    context['add_item_placeholder'] = _('add task').capitalize()
    return context


