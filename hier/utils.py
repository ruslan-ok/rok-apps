import requests, json
from datetime import datetime
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import AnonymousUser

from todo.models import Lst
from .models import Folder, Param, get_app_params
from .params import set_aside_visible, set_article_visible


FOLDERS_COLOR = '#b9ffdc'

NAVBAR_BUTTONS = [
    ('site', {'text': 'rusel.by', 'color': 'Yellow', }, ),
    ('home', {'icon': 'home', 'url': 'index', }, ),

    ('add', {'icon': 'plus', 'href': 'create/', 'p1': 'folder.id', }, ),
    ('move', {'icon': 'share-square', 'href': '/', }, ),
    ('ready', {'text': 'Готово', 'href': 'delete/', 'class': 'w3-right w3-green', }, ),
    ('delete', {'icon': 'trash-alt', 'href': 'delete/', 'class': 'w3-right w3-red', }, ),
    ('param', {'icon': 'cog', 'href': 'parameters/', }, ),

    ('profile', {'text': 'firstof user.get_short_name user.get_username', 'url': 'account:service', 'class': 'w3-right rok-hide-small rok-hide-medium', }, ),
    ('login', {'text': _('Log in'), 'url': 'account:login', 'class': 'w3-right', }, ),
]

#----------------------------------
# Корзина
#----------------------------------
def get_trash(user):
    if Folder.objects.filter(user = user.id, node = 0, model_name = 'trash').exists():
        return Folder.objects.filter(user = user.id, node = 0, model_name = 'trash')[0]
    return Folder.objects.create(user = user, node = 0, model_name = 'trash', name = _('trash').capitalize())


#----------------------------------
# Находится ли указанный элемент в корзине
#----------------------------------
def is_in_trash(folder_id):
    node_id = folder_id
    while node_id:
        node = Folder.objects.filter(id = node_id).get()
        if (node.model_name == 'trash'):
            return True
        node_id = node.node
    return False

#----------------------------------
# Перенести указанный элемент в корзину
#----------------------------------
def put_in_the_trash(user, folder_id):
    file = Folder.objects.filter(id = folder_id).get()
    file.node = get_trash(user).id
    file.save()

#----------------------------------
# Очистить содержимое папки
#----------------------------------
def rmtree(user, folder_id, to_trash = True):
    if not Folder.objects.filter(user = user.id, id = folder_id).exists():
        return
    node = Folder.objects.filter(id = folder_id).get()
    for file in Folder.objects.filter(user = user.id, node = node.id):
        if to_trash:
            file.node = get_trash(user).id
            file.save()
        else:
            file.delete()


#----------------------------------
def get_param(user, default_view = ''):
    if not user.is_authenticated:
        return None
    if Param.objects.filter(user = user.id).exists():
        param = Param.objects.filter(user = user.id).get()
        if (param.cur_view == '') and (default_view != ''):
            param.cur_view = default_view
            param.save()
        return param
    return Param.objects.create(user = user, folder_id = 0, aside = False, article = False, cur_view = default_view)

#----------------------------------
# Контекст для любой страницы
#----------------------------------

# !!!! DEPRECATED !!!!

def get_base_context(request, folder_id, pk, title = '', mode = 'content_form', form = None, make_tree = True, article_enabled = False, app_name = ''):
    context = {}
    if (pk == 0) and (mode == 'content_form'):
        mode = 'content_add'
    context['mode'] = mode
    folder = None
    if request:
        context['site'] = get_current_site(request).name
        param = get_param(request.user)
        if param:
            context['aside_visible'] = ((not article_enabled) or (not param.article)) and param.aside
            context['article_visible'] = param.article and article_enabled

        if (folder_id != 0):
            folder = Folder.objects.filter(user = request.user.id, id = folder_id).get()
    
        if (folder_id == 0) and (pk != 0):
            if Folder.objects.filter(user = request.user.id, content_id = pk).exists():
                folder = Folder.objects.filter(user = request.user.id, content_id = pk)[0]

    if folder and not title:
        title = folder.name

    if folder:
        context['page_id'] = folder.id
    else:
        context['page_id'] = 0

    context['title'] = title
    context['folder'] = folder
    context['content_id'] = pk
    context['pk'] = pk

    if form:
        context['form'] = form
        context['please_correct_one'] = _('Please correct the error below.')
        context['please_correct_all'] = _('Please correct the errors below.')
    """
    context['menu_item_home']    = get_main_menu_item('home')
    context['menu_item_todo']    = get_main_menu_item('todo')
    context['menu_item_note']    = get_main_menu_item('note')
    context['menu_item_news']    = get_main_menu_item('news')
    context['menu_item_store']   = get_main_menu_item('store')
    context['menu_item_trip']    = get_main_menu_item('trip')
    context['menu_item_fuel']    = get_main_menu_item('fuel')
    context['menu_item_apart']   = get_main_menu_item('apart')
    context['menu_item_proj']    = get_main_menu_item('proj')
    context['menu_item_wage']    = get_main_menu_item('wage')
    context['menu_item_admin']   = get_main_menu_item('admin')
    context['menu_item_profile'] = get_main_menu_item('profile')
    context['menu_item_logout']  = get_main_menu_item('logout')
    """
    set_aside_visible(request.user, app_name, False)
    return context

#----------------------------------
# Контекст для любой страницы
#----------------------------------
def get_base_context_ext(request, app_name, content_kind, title, article_enabled = True):
    context = {}
    context['app_name'] = get_app_name(app_name)
    context['restriction'] = None
    app_param = None
    if request:
        app_param = get_app_params(request.user, app_name)
        if app_param:
            if (app_param.content != content_kind):
                app_param.content = content_kind
                app_param.save()
            context['aside_visible'] = ((not article_enabled) or (not app_param.article)) and app_param.aside
            context['article_visible'] = app_param.article and article_enabled
            context['restriction'] = app_param.restriction
            context['sort_dir'] = not app_param.reverse
            context['list_id'] = 0
            if (app_param.restriction == 'list') and app_param.lst:
                lst = Lst.objects.filter(user = request.user.id, id = app_param.lst.id).get()
                title = lst.name
                context['list_id'] = lst.id

    context['title'] = title

    context['please_correct_one'] = _('Please correct the error below.')
    context['please_correct_all'] = _('Please correct the errors below.')
    
    context['complete_icon'] = 'todo/icon/complete.png'
    context['uncomplete_icon'] = 'todo/icon/uncomplete.png'
    
    context['menu_item_home']    = get_main_menu_item('home')
    context['menu_item_todo']    = get_main_menu_item('todo')
    context['menu_item_note']    = get_main_menu_item('note')
    context['menu_item_news']    = get_main_menu_item('news')
    context['menu_item_store']   = get_main_menu_item('store')
    context['menu_item_trip']    = get_main_menu_item('trip')
    context['menu_item_fuel']    = get_main_menu_item('fuel')
    context['menu_item_apart']   = get_main_menu_item('apart')
    context['menu_item_proj']    = get_main_menu_item('proj')
    context['menu_item_wage']    = get_main_menu_item('wage')
    context['menu_item_admin']   = get_main_menu_item('admin')
    context['menu_item_profile'] = get_main_menu_item('profile')
    context['menu_item_logout']  = get_main_menu_item('logout')
    
    
    APPS = [
        ('home',    'home',        '/'),
        ('todo',    'application', '/todo/'),
        ('note',    'note',        '/note/'),
        ('news',    'news',        '/news/'),
        ('store',   'key',         '/store/'),
        ('trip',    'car',         '/trip/'),
        ('fuel',    'gas',         '/fuel/'),
        ('apart',   'apartment',   '/apart/'),
        ('proj',    'cost',        '/proj/'),
        ('wage',    'work',        '/wage/'),
        ('admin',   'admin',       '/admin/'),
        ('profile', 'user',        '/account/profile/'),
        ('logout',  'exit',        '/account/logout/'),
    ]

    apps = []
    for app in APPS:
        apps.append({'href': app[2], 'icon': 'rok/icon/' + app[1] + '.png', 'name': get_main_menu_item(app[0])})
    context['apps'] = apps

    set_aside_visible(request.user, app_name, False)
    if content_kind:
        kind = content_kind
        if (content_kind != 'main'):
            kind = content_kind + '_list'
        save_last_visited(request.user, app_name + ':' + kind, app_name, title)
    return app_param, context

#----------------------------------
# Парная запись в Folder для сущности контента
#----------------------------------
def check_file_for_content(user, folder_id, pk, content_name, content_code, is_new):
    node = Folder.objects.filter(user = user.id, id = folder_id).get()
    redirect_id = folder_id
    if is_new:
        # При добавлении новой записи folder_id - вышестоящая папка
        Folder.objects.create(user = user,
                              node = folder_id,
                              name = content_name,
                              code = content_code,
                              content_id = pk,
                              creation = datetime.now(),
                              last_mod = datetime.now(),
                              icon = node.icon,
                              color = node.color,
                              model_name = node.model_name)
    else:
        # При редактировании записи folder_id - это ссылка на folder, сопоставленный с записью контента
        folder = Folder.objects.filter(user = user.id, id = folder_id, model_name = node.model_name, content_id = pk).get()
        redirect_id = folder.node
        folder.name = content_name
        folder.code = content_code
        folder.save()
    return redirect_id
        

#----------------------------------
def save_folder_id(user, folder_id):
    if Param.objects.filter(user = user.id).exists():
        param = Param.objects.filter(user = user.id).get()
        param.folder_id = folder_id
        param.save()
    else:
        Param.objects.create(user = user, folder_id = folder_id)
        
#----------------------------------
def get_folder_id(user_id):
    if Param.objects.filter(user = user_id).exists():
        param = Param.objects.filter(user = user_id).get()
        return param.folder_id
    else:
        return 0

#----------------------------------
def process_common_commands(request, app_name):
    if (request.method == 'POST'):
        if 'aside_open' in request.POST:
            set_article_visible(request.user, app_name, False)
            set_aside_visible(request.user, app_name, True)
            return True
        if 'aside_close' in request.POST:
            set_aside_visible(request.user, app_name, False)
            return True
        if 'article_open' in request.POST:
            set_aside_visible(user, app_name, False)
            set_article_visible(request.user, app_name, True)
            return True
        if 'article_close' in request.POST:
            set_article_visible(request.user, app_name, False)
            return True
    return False

def save_last_visited(user, url, app, page):
    if not page:
        return
    param = get_param(user)
    if param:
        param.last_url = url
        param.last_app = get_app_name(app)
        param.last_page = page
        param.save()

def get_app_name(id):
    if (id == 'rusel'):
        return 'rusel.by'
    if (id == 'apart'):
        return _('communal').capitalize()
    if (id == 'fuel'):
        return _('fuelings').capitalize()
    if (id == 'hier'):
        return _('hierarchy').capitalize()
    if (id == 'note'):
        return _('notes').capitalize()
    if (id == 'news'):
        return _('news').capitalize()
    if (id == 'pir'):
        return _('problems and solutions').capitalize()
    if (id == 'proj'):
        return _('expenses').capitalize()
    if (id == 'store'):
        return _('passwords').capitalize()
    if (id == 'todo'):
        return _('tasks').capitalize()
    if (id == 'trip'):
        return _('trips').capitalize()
    if (id == 'wage'):
        return _('work').capitalize()
    return None

def get_main_menu_item(id):
    name = get_app_name(id)
    if name:
        return name
    if (id == 'home'):
        return _('home').capitalize()
    if (id == 'news'):
        return _('news').capitalize()
    if (id == 'admin'):
        return _('admin').capitalize()
    if (id == 'profile'):
        return _('profile').capitalize()
    if (id == 'logout'):
        return _('log out').capitalize()
    return None


def sort_data(data, sort, reverse):
    if not data:
        return data

    sort_fields = sort.split()
    if reverse:
        revers_list = []
        for sf in sort_fields:
            if (sf[0] == '-'):
                revers_list.append(sf[1:])
            else:
                revers_list.append('-' + sf)
        sort_fields = revers_list

    #raise Exception(sort, reverse, sort_fields)
    if (len(sort_fields) == 1):
        data = data.order_by(sort_fields[0])
    elif (len(sort_fields) == 2):
        data = data.order_by(sort_fields[0], sort_fields[1])
    elif (len(sort_fields) == 3):
        data = data.order_by(sort_fields[0], sort_fields[1], sort_fields[2])

    return data


def get_rate_on_date(currency, date):
    # https://www.nbrb.by/api/exrates/rates/145?ondate=2020-10-10
    url = 'https://www.nbrb.by/api/exrates/rates/{}?ondate={}-{}-{}'.format(currency, date.year, date.month, date.day)
    resp = requests.get(url)
    try:
        data = resp.json()
    except json.JSONDecodeError:
        return None
    return data['Cur_OfficialRate']

def extract_get_params(request):
    q = request.GET.get('q')
    if not q:
        q = ''
    p = request.GET.get('page')
    if not p:
        p = ''
    ret = ''
    if q:
        ret += 'q={}'.format(q)
    if p:
        if q:
            ret += '&'
        ret += 'page={}'.format(p)
    if ret:
        ret = '?' + ret
    return ret


