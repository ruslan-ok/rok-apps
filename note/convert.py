from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from hier.models import Folder
from todo.models import Grp, Lst
from .models import Note

def get_lst(user, folder_id, app):
    path = []
    ok = True
    lst_folder = None
    while folder_id:
        if not Folder.objects.filter(id = folder_id).exists():
            ok = False
            break
        f = Folder.objects.filter(id = folder_id).get()
        if not lst_folder:
            lst_folder = f
        else:
            if (app == 'news') and (f.name == 'Записи'):
                break
            if (f.model_name[:9] == 'note:note') or (f.model_name[:9] == 'note:news'):
                if (f.name == 'Заметки'):
                    break
                path.append(f)
        folder_id = f.node
        
    if (not ok) or (not lst_folder):
        return ok, None
        
    grp = None
    for f in reversed(path):
        if Grp.objects.filter(user = user.id, app = app, node = grp, name = f.name).exists():
            grp = Grp.objects.filter(user = user.id, app = app, node = grp, name = f.name).get()
        else:
            grp = Grp.objects.create(user = user, app = app, node = grp, sort = f.code, is_open = f.is_open, name = f.name)

    if Lst.objects.filter(user = user.id, app = app, grp = grp, name = lst_folder.name).exists():
        return ok, Lst.objects.filter(user = user.id, app = app, grp = grp, name = lst_folder.name).get()

    return ok, Lst.objects.create(user = user, app = app, grp = grp, name = lst_folder.name, sort = lst_folder.code)

def convert(request):
    for e in Note.objects.all():
        e.lst = None
        e.kind = 'note'
        e.save()
    Lst.objects.filter(app = 'note').delete()
    Lst.objects.filter(app = 'news').delete()
    Grp.objects.filter(app = 'note').delete()
    Grp.objects.filter(app = 'news').delete()
    for e in Note.objects.all():
        ok = False
        is_news = False
        lst = None
        app = 'note'
        for f in Folder.objects.filter(user = e.user.id, content_id = e.id):
            if (f.model_name[:5] == 'note:'):
                app = 'note'
                if (f.model_name[:9] == 'note:news'):
                    app = 'news'
                ok, lst = get_lst(e.user, f.node, app)
                if ok:
                    break
        if ok:
            e.lst = lst
            e.kind = app
            e.save()
    return HttpResponseRedirect(reverse('note:note_list'))
