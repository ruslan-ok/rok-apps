from django.utils.translation import gettext_lazy as _
from todo.models import Lst
from hier.models import get_app_params

#----------------------------------
def set_aside_visible(user, app_name, visible):
    app_param = get_app_params(user, app_name)
    if not app_param:
        return

    app_param.aside = visible
    app_param.save()

#----------------------------------
def set_article_visible(user, app_name, visible):
    app_param = get_app_params(user, app_name)
    if not app_param:
        return

    app_param.article = visible
    app_param.save()

#----------------------------------
def set_restriction(user, app_name, restriction, lst_id = 0):
    app_param = get_app_params(user, app_name)
    if not app_param:
        return

    app_param.restriction = restriction
    if (restriction == 'list') and lst_id:
        if Lst.objects.filter(user = user.id, app = app_name, id = lst_id).exists():
            app_param.lst = Lst.objects.filter(user = user.id, app = app_name, id = lst_id).get()
    app_param.aside = False
    app_param.save()

#----------------------------------
def set_content(user, app_name, content):
    app_param = get_app_params(user, app_name)
    if app_param:
        app_param.content = content
        app_param.save()

#----------------------------------
def set_article_kind(user, app_name, article_kind, article_id = 0):
    app_param = get_app_params(user, app_name)
    if not app_param:
        return

    app_param.kind = article_kind
    app_param.art_id = article_id
    if not article_id:
        app_param.article = False
    else:
        app_param.article = True
        app_param.aside = False
    app_param.save()

#----------------------------------
def set_sort_mode(user, app_name, sort_mode):
    app_param = get_app_params(user, app_name)
    if not app_param:
        return

    app_param.sort = sort_mode
    app_param.save()

#----------------------------------
def toggle_sort_dir(user, app_name):
    app_param = get_app_params(user, app_name)
    if not app_param:
        return

    app_param.reverse = not app_param.reverse
    app_param.save()

#----------------------------------
def get_search_mode(query):
    if not query:
        return 0
    if (len(query) > 1) and (query[0] == '@') and (query.find(' ') == -1):
        return 2
    else:
        return 1

def get_search_info(query):
    search_mode = get_search_mode(query)
    if (search_mode == 1):
        return query
    elif (search_mode == 2):
        return query[1:]
    else:
        return ''
