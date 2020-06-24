from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from hier.utils import get_base_context, get_trash, rmtree
from hier.models import Folder
from note.models import List, View, Filter, Note
from store.models import Group, Entry
from .etalon import menu

#----------------------------------
# Convert
#----------------------------------
def convert(request):
    #rmtree(request.user, get_trash(request.user).id, False)

    root = Folder.objects.filter(user = request.user.id, model_name = 'note:note', node = 0).get()
    rmtree(request.user, root.id, False)
    build_tree_notes(request.user, root)
    
    root = Folder.objects.filter(user = request.user.id, model_name = 'note:news', node = 0).get()
    rmtree(request.user, root.id, False)
    build_tree_news(request.user, root)

    root = Folder.objects.filter(user = request.user.id, model_name = 'store:entry', node = 0).get()
    rmtree(request.user, root.id, False)
    build_tree_entry(request.user, root)

    return HttpResponseRedirect(reverse('hier:folder_list', args = [0]))

#----------------------------------
# Build Tree for Notes
#----------------------------------
def build_tree_notes(user, root):
    for view in View.objects.filter(user = user, chrono = False):
        f = Folder.objects.create(user = user,
            node = root.id,
            code = view.code.replace('\\', ''),
            name = view.name.replace('\\', ''),
            creation = datetime.now(),
            last_mod = datetime.now(),
            is_open = False,
            icon = root.icon,
            color = root.color,
            model_name = root.model_name,
            content_id = 0)

        for flt in Filter.objects.filter(view = view.id, entity = 1).order_by('npp'):
            list = List.objects.filter(id = flt.value).get()
            l = Folder.objects.create(user = user,
                node = f.id,
                code = list.code.replace('\\', ''),
                name = list.name.replace('\\', ''),
                creation = datetime.now(),
                last_mod = datetime.now(),
                is_open = False,
                icon = root.icon,
                color = list.color,
                model_name = root.model_name,
                content_id = 0)

            for note in Note.objects.filter(user = user, list = list.id).order_by('code', 'name'):
                #note.user = user
                #note.save()
                Folder.objects.create(user = user,
                    node = l.id,
                    code = note.code.replace('\\', ''),
                    name = note.name.replace('\\', ''),
                    creation = note.publ,
                    last_mod = datetime.now(),
                    is_open = False,
                    icon = root.icon,
                    color = l.color,
                    model_name = root.model_name,
                    content_id = note.id)

#----------------------------------
# Build Tree for News
#----------------------------------
def build_tree_news(user, root):
    for view in View.objects.filter(user = user, chrono = True):
        for flt in Filter.objects.filter(view = view.id, entity = 1).order_by('npp'):
            list = List.objects.filter(id = flt.value).get()
            for note in Note.objects.filter(user = user, list = list.id).order_by('code', 'name'):
                #note.user = user
                #note.save()
                Folder.objects.create(user = user,
                    node = root.id,
                    code = note.code.replace('\\', ''),
                    name = note.name.replace('\\', ''),
                    creation = note.publ,
                    last_mod = datetime.now(),
                    is_open = False,
                    icon = root.icon,
                    color = root.color,
                    model_name = root.model_name,
                    content_id = note.id)

#----------------------------------
# Build Tree for Entries
#----------------------------------
def build_tree_entry(user, root):
    for grp in Group.objects.filter(user = user):
        g = Folder.objects.create(user = user,
            node = root.id,
            code = grp.code.replace('\\', ''),
            name = grp.name.replace('\\', ''),
            creation = grp.creation,
            last_mod = grp.last_mod,
            is_open = False,
            icon = root.icon,
            color = root.color,
            model_name = root.model_name,
            content_id = 0)
        for entry in Entry.objects.filter(group = grp.id):
            #entry.user = user
            #entry.save()
            Folder.objects.create(user = user,
                node = g.id,
                code = entry.username.replace('\\', ''),
                name = entry.title.replace('\\', ''),
                creation = entry.creation,
                last_mod = entry.last_mod,
                is_open = False,
                icon = root.icon,
                color = root.color,
                model_name = root.model_name,
                content_id = entry.id)

#----------------------------------
# Statistics
#----------------------------------
def statistics(request):    
    with_content = 0
    for folder in Folder.objects.filter(user = request.user.id):
        if folder.content_id:
            with_content = with_content + 1

    if with_content:
        context = get_base_context(request, 0, 0, 'Конвертер')
        context['result'] = ['Количество файлов с контентом: ' + str(with_content),
                             ]
    
        template = loader.get_template('convert.html')
        return HttpResponse(template.render(context, request))

    notes_qty = 0
    lists_qty = 0
    views_qty = 0
    filters_qty = 0
    notes_list_qty = 0

    for view in View.objects.all():
        views_qty = views_qty + 1
    
    for list in List.objects.all():
        lists_qty = lists_qty + 1
    
    for filter in Filter.objects.all():
        filters_qty = filters_qty + 1
    
    for note in Note.objects.all():
        notes_qty = notes_qty + 1
        if note.list:
            notes_list_qty = notes_list_qty + 1
    
    context = get_base_context(request, 0, 0, 'Конвертер')
    context['result'] = ['Представлений: ' + str(views_qty),
                         'Списков: ' + str(lists_qty),
                         'Фильтров: ' + str(filters_qty),
                         'Заметок: ' + str(notes_qty),
                         'Заметок в списках: ' + str(notes_list_qty),
                         'user.id: ' + str(request.user.id),
                         ]

    template = loader.get_template('statistics.html')
    return HttpResponse(template.render(context, request))


def check_menu(user, node_id, branch):
    p = []
    m = []
    n = []
    for item in branch:
        name = item[0]
        code = str(item[1])
        icon = item[2]
        color = item[3]
        app = item[4]
        if Folder.objects.filter(user = user.id, node = node_id, name = name, model_name = app).exists():
            folder = Folder.objects.filter(user = user.id, node = node_id, name = name, model_name = app).get()
            if (folder.code == code) and (folder.icon == icon) and (folder.color == color):
                p.append(name)
            else:
                m.append(name)
                folder.code = code
                folder.icon = icon
                folder.color = color
                folder.save()
        else:
            if Folder.objects.filter(user = user.id, node = 0, name = name, model_name = app).exists():
                folder = Folder.objects.filter(user = user.id, node = 0, name = name, model_name = app).get()
                m.append(name)
                folder.node = node_id
                folder.code = code
                folder.icon = icon
                folder.color = color
                folder.save()
            else:
                n.append(name)
                folder = Folder.objects.create(user = user, node = node_id, name = name, model_name = app, code = code, icon = icon, color = color)
        ret = check_menu(user, folder.id, item[5])
        p.append(ret[0])
        m.append(ret[1])
        n.append(ret[2])
    return [p, m, n]

def clear_folder(user, node_id, name):
    if Folder.objects.filter(user = user.id, node = node_id, name = name).exists():
        folder = Folder.objects.filter(user = user.id, node = node_id, name = name).get()
        rmtree(user, folder.id, False)

def etalon(request):
    clear_folder(request.user, 0, 'Проезд')
    clear_folder(request.user, 0, 'Восстановить')
    clear_folder(request.user, 0, 'Корзина')

    res = check_menu(request.user, 0, menu)

    return HttpResponseRedirect(reverse('hier:folder_list', args = [0]))



