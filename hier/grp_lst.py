from django.shortcuts import get_object_or_404
from django.db.models import Q

from todo.models import Grp, Lst
from todo.forms import GrpForm, LstForm
from hier.params import set_article_visible, set_aside_visible
from hier.search import SearchResult

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
        if ('item_save' in request.POST):
            form = GrpForm(request.user, app_name, request.POST, instance = ed_grp)
            if form.is_valid():
                grp = form.save(commit = False)
                grp.user = request.user
                form.save()
                return True
        elif ('item_delete' in request.POST):
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
        if ('item_save' in request.POST):
            form = LstForm(request.user, app_name, request.POST, instance = ed_lst)
            if form.is_valid():
                lst = form.save(commit = False)
                lst.user = request.user
                form.save()
                return True
        elif ('item_delete' in request.POST):
            if can_delete:
                ed_lst.delete()
                set_article_visible(request.user, app_name, False)
            return True

    if not form:
        form = LstForm(request.user, app_name, instance = ed_lst)

    context['form'] = form
    return False


class TreeNode():
    id = 0
    name = ''
    level = 0
    is_list = False
    is_open = False
    qty = 0
    url = 'list/' + str(id) + '/'

    def __init__(self, id, name, level, is_list = False, is_open = False, qty = 0):
        self.id = id
        self.name = name
        self.level = level
        self.is_list = is_list
        self.is_open = is_open
        self.qty = qty
        url = 'list/' + str(id) + '/'

    def __str__(self):
        ret = str(self.level) + '/' + str(self.id) + ' "' + self.name + '" '
        if self.is_node:
            if self.is_open:
                ret = ret + '[-]'
            else:
                ret = ret + '[+]'
        return ret


def scan_level(tree, user_id, node_id, level, app_name):
    if (node_id == 0):
        node_id = None
    for grp in Grp.objects.filter(user = user_id, app = app_name, node = node_id).order_by('sort', 'name'):
        tree.append(TreeNode(grp.id, grp.name, level, False, grp.is_open))
        if grp.is_open:
            for lst in Lst.objects.filter(user = user_id, grp = grp.id).order_by('sort', 'name'):
                tree.append(TreeNode(lst.id, lst.name, level + 1, True, False))
            scan_level(tree, user_id, grp.id, level + 1, app_name)


def build_tree(user_id, app_name):
    tree = []
    scan_level(tree, user_id, 0, 0, app_name)
    for lst in Lst.objects.filter(user = user_id, grp = None, app = app_name).order_by('sort', 'name'):
        tree.append(TreeNode(lst.id, lst.name, 0, True, False))
    return tree

def search(user, app_name, query):
    result = SearchResult(query)
    lookups = Q(name__icontains=query)
    groups = Grp.objects.filter(user = user.id, app = app_name).filter(lookups).distinct()
    for group in groups:
        result.add(app_name, 'group', group.id, group.created.date(), group.name, '', False)
    lists = Lst.objects.filter(user = user.id, app = app_name).filter(lookups).distinct()
    for lst in lists:
        result.add(app_name, 'list', lst.id, lst.created.date(), lst.name, '', False)
    return result.items


