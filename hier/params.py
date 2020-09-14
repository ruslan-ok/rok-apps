from django.utils.translation import gettext_lazy as _
from .models import AppParam
from todo.models import Lst

#----------------------------------
def get_app_params(user, app):
    if not user.is_authenticated:
        return None

    if not AppParam.objects.filter(user = user.id, app = app).exists():
        return AppParam.objects.create(user = user, app = app, aside = False, article = False, content = '', kind = '', lst = None, art_id = 0)

    return AppParam.objects.filter(user = user.id, app = app).get()

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
    if (len(query) > 1) and (query[0] == '#') and (query.find(' ') == -1):
        return 2
    else:
        return 1

def get_search_info(query):
    search_mode = get_search_mode(query)
    if (search_mode == 1):
        return _('contained').capitalize() + ' "' + query + '"'
    elif (search_mode == 2):
        return _('contained category').capitalize() + ' "' + query[1:] + '"'
    else:
        return ''
