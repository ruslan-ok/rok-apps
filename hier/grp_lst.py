from django.shortcuts import get_object_or_404
from todo.models import Grp, Lst
from todo.forms import GrpForm, LstForm
from hier.params import set_article_visible, set_aside_visible

def group_add(user, app_name, name):
    grp = Grp.objects.create(user = user, app = app_name, name = name)
    return grp.id

def group_details(request, context, pk, app_name):
    if not Grp.objects.filter(id = pk, user = request.user.id, app = app_name).exists():
        set_aside_visible(request.user, app_name, False)
        return False

    ed_grp = Grp.objects.filter(id = pk, user = request.user.id, app = app_name).get()
    
    form = None
    if (request.method == 'POST'):
        if ('group-save' in request.POST):
            form = GrpForm(request.user, app_name, request.POST, instance = ed_grp)
            if form.is_valid():
                grp = form.save(commit = False)
                grp.user = request.user
                form.save()
                return True
        elif ('article_delete' in request.POST):
            if group_delete(ed_grp):
                set_article_visible(request.user, app_name, False)
            return True

    if not form:
        form = GrpForm(request.user, app_name, instance = ed_grp)

    context['form'] = form
    return False

def group_toggle(user, app_name, pk):
    grp = get_object_or_404(Grp.objects.filter(user = user.id, id = pk, app = app_name))
    grp.is_open = not grp.is_open
    grp.save()
    set_aside_visible(user, app_name, True)

def group_delete(ed_grp):
    if Grp.objects.filter(node = ed_grp.id).exists() or Lst.objects.filter(grp = ed_grp.id).exists():
        return False
    ed_grp.delete()
    return True

def list_add(user, app_name, name):
    lst = Lst.objects.create(user = user, app = app_name, name = name)
    return lst.id

def list_details(request, context, pk, app_name, can_delete):
    if not Lst.objects.filter(id = pk, user = request.user.id, app = app_name).exists():
        set_aside_visible(request.user, app_name, False)
        return False

    ed_lst = Lst.objects.filter(id = pk, user = request.user.id, app = app_name).get()
    
    form = None
    if (request.method == 'POST'):
        if ('list-save' in request.POST):
            form = LstForm(request.user, app_name, request.POST, instance = ed_lst)
            if form.is_valid():
                lst = form.save(commit = False)
                lst.user = request.user
                form.save()
                return True
        elif ('article_delete' in request.POST):
            if can_delete:
                ed_lst.delete()
                set_article_visible(request.user, app_name, False)
            return True

    if not form:
        form = LstForm(request.user, app_name, instance = ed_lst)

    context['form'] = form
    return False


