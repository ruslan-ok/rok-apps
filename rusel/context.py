from django.utils.translation import gettext_lazy as _
from rest_framework.renderers import JSONRenderer

from rusel.apps import get_app_name, get_app_params, get_beta, get_apps_list
from task.models import TaskGrp, ATask
from task.serializers import TaskGrpSerializer

def get_base_context(request, app, detail, title):
    context = {}
    context['app'] = app
    context['app_name'] = get_app_name(app)
    context['restriction'] = None
    context['beta'] = get_beta(request.user)
    app_param = None
    title_1 = title_2 = url = ''
    if title:
        if type(title) is str:
            title_1 = title
        if type(title) is tuple:
            if (len(title) > 0):
                title_1 = title[0]
            if (len(title) > 1):
                title_2 = title[1]
    app_param = get_app_params(request.user, app)
    context['article_visible'] = detail
    context['restriction'] = app_param.restriction
    context['sort_dir'] = not app_param.reverse
    context['list_id'] = 0
    url = app_param.restriction
    if (app_param.restriction == 'list') and app_param.lst:
        lst = TaskGrp.objects.filter(user=request.user.id, id=app_param.lst.id).get()
        title_1 = ''
        title_2 = lst.name
        context['list_id'] = lst.id
        url = 'list/' + str(lst.id)

    if not title_1 and not title_2:
        context['title'] = ''
    if title_1 and not title_2:
        context['title'] = _(title_1).capitalize()
    if not title_1 and title_2:
        context['title'] = title_2
    if title_1 and title_2:
        context['title'] = '{} [{}]'.format(_(title_1).capitalize(), title_2)

    context['please_correct_one'] = _('Please correct the error below.')
    context['please_correct_all'] = _('Please correct the errors below.')
    
    context['complete_icon'] = 'todo/icon/complete.png'
    context['uncomplete_icon'] = 'todo/icon/uncomplete.png'
    
    context['apps'] = get_apps_list(request.user)

    #if url:
    #    save_last_visited(request.user, app + '/' + url, app, title_1, title_2)

    groups = TaskGrp.objects.filter(user=request.user.id, app=app)
    context['groups'] = JSONRenderer().render(TaskGrpSerializer(groups, many=True, context={'request': request}).data)

    if app_param.sort and (app_param.sort in SORT_MODE_DESCR):
        context['sort_mode'] = SORT_MODE_DESCR[app_param.sort].capitalize()
    context['add_item_placeholder'] = _('add task').capitalize()
    return context


