import requests
from datetime import datetime
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import AnonymousUser

from note.utils import get_ready_folder
from .models import Folder, Param
from .tree import build_tree
from .params import get_app_params, set_aside_visible, set_article_visible


FOLDERS_COLOR = '#b9ffdc'

NAVBAR_BUTTONS = [
    ('site', {'text': 'rusel.by', 'color': 'Yellow', }, ),
    ('home', {'icon': 'home', 'url': 'index', }, ),

    ('add', {'icon': 'plus', 'href': 'create/', 'p1': 'folder.id', }, ),
    ('move', {'icon': 'share-square', 'href': '/', }, ),
    ('ready', {'text': 'Готово', 'href': 'delete/', 'class': 'w3-right w3-green', }, ),
    ('delete', {'icon': 'trash-alt', 'href': 'delete/', 'class': 'w3-right w3-red', }, ),
    ('search', {'icon': 'search', 'url': 'hier:folder_list', 'p1': 'folder.id', }, ),
    ('param', {'icon': 'cog', 'href': 'parameters/', }, ),

    ('root', {'icon': 'folder-open', 'url': 'hier:folder_list', 'p1': '0', 'color': FOLDERS_COLOR, }, ),
    ('dir', {'icon': 'list-alt', 'url': 'hier:folder_dir', 'p1': 'folder.id', 'color': FOLDERS_COLOR, }, ),
    ('prop', {'icon': 'edit', 'url': 'hier:folder_form', 'p1': 'folder.id', 'color': FOLDERS_COLOR, }, ),
    ('folder_add', {'icon': 'folder-plus', 'url': 'hier:folder_add', 'p1': 'folder.id', 'color': FOLDERS_COLOR, }, ),

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
# Buttons
#----------------------------------

# Заметку можно переместить в список "Готово"
def note_ready(user_id, folder):
    if not folder:
        return False
    ready = get_ready_folder(user_id, folder.id)
    return ready and (ready.id != folder.node)

# Форма с контентом (за исключением формы заметки, которую можно переместить в список "Готово")
def is_content_form(mode, user_id, folder):
    return (mode == 'content_form') and (not note_ready(user_id, folder)) and folder

# Удалять можно только пустую папку
def folder_is_empty(folder_id):
    return True # not Folder.objects.filter(node = folder_id).exists()

# Папка, которую можно удалить
def is_folder_form(mode, folder):
    return (mode == 'folder')  and folder and folder_is_empty(folder.id) #and (folder.content_id == 0)

# Надо ли показывать кнопку
def is_button_visible(btn_name, user, mode, folder):

    if (btn_name == 'site'):
        return (not user.is_authenticated) or (mode == 'dialog')
    
    if (btn_name == 'login'):
        return (not user.is_authenticated) and (mode == 'content_list')
    
    if (btn_name == 'home'):
        return user.is_authenticated and (folder or (mode == 'dir')) #and ((mode == 'dir') or (mode == 'folder'))

    if (btn_name == 'search'):
        return user.is_authenticated and (((mode == 'content_list') and folder) ) # or ((mode == 'dir') and folder and (folder.model_name != '')))
    
    if (btn_name == 'param'):
        return user.is_authenticated and (mode == 'content_list') and folder 
    
    if (btn_name == 'add'):
        return user.is_authenticated and (mode == 'content_list') and folder
    
    if (btn_name == 'move'):
        return user.is_authenticated and folder and ((mode == 'content_form') or (mode == 'folder'))
    
    if (btn_name == 'delete'):
        return user.is_authenticated and (is_content_form(mode, user.id, folder) or is_folder_form(mode, folder)) 

    if (btn_name == 'ready'):
        return user.is_authenticated and (mode == 'content_form') and note_ready(user.id, folder)

    if (btn_name == 'root'):
        return False # user.is_authenticated and (mode == 'dir') and (folder)
    
    if (btn_name == 'dir'):
        return user.is_authenticated and ((mode == 'content_list') or (mode == 'folder')) #and ((not folder) or (folder.model_name != 'trip:trip'))
    
    if (btn_name == 'prop'):
        return user.is_authenticated and (folder) and (mode != 'folder') and (mode != 'content_add')

    if (btn_name == 'folder_add'):
        return user.is_authenticated and ((mode == 'dir') or ((mode == 'content_list') and folder and folder.get_folder_enabled()))

    return False

#----------------------------------
def make_href(url, p1, p2 = None):
    if url and (p1 != None) and (p2 != None):
        return reverse(url, args = [p1, p2])
    if url and (p1 != None):
        return reverse(url, args = [p1])
    if url:
        return reverse(url)
    return None

#----------------------------------
def make_button(folder_id, btn):
    ret = btn[1].copy()
    href = btn[1].get('href')

    if not href:
        url = btn[1].get('url')
        s1 = btn[1].get('p1')
        if (s1 == 'folder.id'):
            p1 = folder_id
        elif s1:
            p1 = int(s1)
        else:
            p1 = None
        
        href = make_href(url, p1)

    ret['href'] = href

    return ret

#----------------------------------
def get_buttons(user, folder_id, mode, folder):
    buttons = []
    for btn in NAVBAR_BUTTONS[0:2]:
        if is_button_visible(btn[0], user, mode, folder):
            buttons.append(make_button(folder_id, btn))

    chain = []
    cur_id = folder_id
    first = (mode != 'content_add')
    while (cur_id != 0):
        if Folder.objects.filter(user = user.id, id = cur_id).exists():
            node = Folder.objects.filter(user = user.id, id = cur_id)[0]
            if not first and ((not node.content_id) or node.is_folder):
                chain.append(node)
            first = False
            cur_id = node.node
        else:
            break

    for node in reversed(chain):
        link = {}
        link['href'] = make_href('hier:folder_list', node.id)
        link['text'] = node.name
        buttons.append(link)

    for btn in NAVBAR_BUTTONS[2:]:
        if is_button_visible(btn[0], user, mode, folder):
            buttons.append(make_button(folder_id, btn))

    return buttons

#----------------------------------
def get_moves(user, mode, folder_id, tree, folder):
    moves = []

    if is_button_visible('move', user, mode, folder):
        for node in tree:
            moves.append({ 'href': make_href('hier:folder_move', folder_id, node.id), 'name': node.name, 'icon': node.icon, 'color': node.color })

    return moves

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

        if make_tree:
            tree = build_tree(request.user.id, 0)
        else:
            tree = []
        context['tree'] = tree

        context['buttons'] = get_buttons(request.user, folder_id, mode, folder)
        context['moves'] = get_moves(request.user, mode, folder_id, tree, folder)

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
    context['menu_item_trash']   = get_main_menu_item('trash')
    context['menu_item_admin']   = get_main_menu_item('admin')
    context['menu_item_profile'] = get_main_menu_item('profile')
    context['menu_item_logout']  = get_main_menu_item('logout')
    set_aside_visible(request.user, app_name, False)
    return context

#----------------------------------
# Контекст для любой страницы
#----------------------------------
def get_base_context_ext(request, app_name, content_kind, title, article_enabled = True):
    context = {}
    context['title'] = title
    context['app_name'] = get_app_name(app_name)
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

    context['please_correct_one'] = _('Please correct the error below.')
    context['please_correct_all'] = _('Please correct the errors below.')

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
    context['menu_item_trash']   = get_main_menu_item('trash')
    context['menu_item_admin']   = get_main_menu_item('admin')
    context['menu_item_profile'] = get_main_menu_item('profile')
    context['menu_item_logout']  = get_main_menu_item('logout')
    set_aside_visible(request.user, app_name, False)
    if content_kind:
        save_last_visited(request.user, app_name + ':' + content_kind + '_list', app_name, title)
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
    if (id == 'trash'):
        return _('trash').capitalize()
    if (id == 'admin'):
        return _('admin').capitalize()
    if (id == 'profile'):
        return _('profile').capitalize()
    if (id == 'logout'):
        return _('log out').capitalize()
    return None


def sort_data(data, sort, reverse):
    sort_fields = sort.split()
    if reverse:
        revers_list = []
        for sf in sort_fields:
            revers_list.append('-' + sf)
        sort_fields = revers_list

    if (len(sort_fields) == 1):
        data = data.order_by(sort_fields[0])
    elif (len(sort_fields) == 2):
        data = data.order_by(sort_fields[0], sort_fields[1])
    elif (len(sort_fields) == 3):
        data = data.order_by(sort_fields[0], sort_fields[1], sort_fields[2])

    return data


def get_rate_on_date(currency, date):
    url = 'https://www.nbrb.by/api/exrates/rates/{}?ondate={}-{}-{}'.format(currency, date.year, date.month, date.day)
    resp = requests.get(url)
    data = resp.json()
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


