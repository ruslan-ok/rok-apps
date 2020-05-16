from datetime import datetime
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.shortcuts import get_current_site

from note.utils import get_ready_folder
from .models import Folder, Param
from .tree import build_tree


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
# Контекст для любой страницы
#----------------------------------
def get_base_context(request, folder_id, pk, title = '', mode = 'content_form'):
    context = {}
    if (pk == 0) and (mode == 'content_form'):
        mode = 'content_add'
    context['mode'] = mode
    folder = None
    if request:
        context['site_header'] = get_current_site(request).name

        if (folder_id != 0):
            folder = Folder.objects.filter(user = request.user.id, id = folder_id).get()
    
        if (folder_id == 0) and (pk != 0):
            if Folder.objects.filter(user = request.user.id, content_id = pk).exists():
                folder = Folder.objects.filter(user = request.user.id, content_id = pk)[0]

        tree = build_tree(request.user.id, 0)
        context['tree'] = tree

        context['buttons'] = get_buttons(request.user, folder_id, mode, folder)
        context['moves'] = get_moves(request.user, mode, folder_id, tree, folder)

    if folder and not title:
        title = folder.name

    context['title'] = title
    context['folder'] = folder
    context['content_id'] = pk
    context['pk'] = pk
    return context

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








