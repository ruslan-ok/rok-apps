from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from family.models import (FamTreeUser, FamTree, IndividualRecord, Params, )
from family.config import app_config
from family.views.base import GenealogyContext

@login_required(login_url='account:login')
def diagram(request, ft: int):
    get_object_or_404(FamTreeUser.objects.filter(user_id=request.user.id, tree_id=ft))
    tree = get_object_or_404(FamTree.objects.filter(id=ft))
    indi_list = []
    path_list = []
    indi = None
    indi_ids = None
    if ('indi' not in request.GET):
        indi = Params.get_cur_indi(request.user, tree)
        indi_id = int(indi.id)
        indi_id_list = [indi_id]
    else:
        indi_ids = request.GET['indi']
        if (',' not in indi_ids):
            indi_id = int(indi_ids)
            indi_id_list = [indi_id]
        else:
            indi_id_list = [int(x) for x in indi_ids.split(',')]
            indi_id = indi_id_list[0]
    if IndividualRecord.objects.filter(id=indi_id).exists():
        indi = IndividualRecord.objects.filter(id=indi_id).get()
        if not FamTreeUser.objects.filter(user_id=request.user.id, tree_id=indi.tree.id).exists():
            indi = None
        else:
            Params.set_cur_indi(indi.tree, indi)
            items_tree = []
            children = indi.get_children()
            children_qnt = len(children)
            child_pos = int(-1 * (children_qnt - 1))
            build_ancestor_tree(items_tree, indi_id_list, None, indi, 0)
            count_ancestor_tree(items_tree, child_pos)
            ix = 1
            iy = items_tree[0][0].pos
            cx = 0
            cy = int(-1 * (children_qnt - 1)) + iy
            for child in children:
                indi_list.append(indi_descr(child, cx, cy))
                path_list.append(path_descr(cy, ix, iy))
                cy += 2
            indi_list.append(indi_descr(indi, ix, iy))
            ix = 2
            while ix <= len(items_tree):
                for ancestor in items_tree[ix-1]:
                    indi_list.append(indi_descr(ancestor.indi, ix, ancestor.pos, ancestor.fam_btn))
                    path_list.append(path_descr(ancestor.child.pos, ix, ancestor.pos))
                ix += 1

    action_list = []
    action_list.append({'name': _('menu').capitalize(), 'w': 100, 'h': 30, 'x': 10, 'y': 10, 'tx': 5, 'ty': 20, 'href': reverse('family:list')})
    action_list.append({'type': 'circle', 'x': 55, 'y': 60, 'path': 'M0,5v-10M5,0h-10', 'onclick': 'zoomIn()'})
    action_list.append({'type': 'circle', 'x': 55, 'y': 90, 'path': 'M5,0h-10', 'onclick': 'zoomOut()'})

    ctx = GenealogyContext()
    ctx.request = request
    ctx.set_config(app_config, 'tree')
    ctx.config.set_view(request)
    if indi:
        ctx.object = indi # To init Page Title
    context = ctx.get_app_context(request.user.id, icon=ctx.config.view_icon)
    context['indi_ids'] = indi_ids
    context['indi_list'] = indi_list
    context['path_list'] = path_list
    context['action_list'] = action_list
    context['tree_id'] = ft
    template = loader.get_template('family/diagram.html')
    return HttpResponse(template.render(context, request))

def indi_descr(indi, x, y, fam_btn=False):
    return {
        'id': indi.id, 
        'name': indi.short_name(), 
        'dates': indi.dates(), 
        'photo': indi.prim_mmr(),
        'fam_btn': fam_btn,
        'x': x * 300, 
        'y': y * 50, 
        'xr': x * 300 + 125, 
        'male': indi.sex=='M',
    }

def path_descr(ay, bx, by):
    return {
        'x': bx * 300 - 100,
        'y': 25 + ay * 50, 
        'lines': [
            'H' + str(bx * 300 - 50),
            'V' + str(25 + by * 50),
            'H' + str(bx * 300)
        ]
    }

class Ancestor:
    def __init__(self, prev, child, indi):
        super().__init__()
        self.indi = indi # IndividualRecord
        self.child = child # Ancestor
        self.prev = prev # Ancestor
        self.father = None
        self.mother = None
        self.pos = None
        self.fam_btn = False

    def __repr__(self) -> str:
        return str(self.pos) + ': ' + self.indi.name()

    def set_pos(self, pos):
        if self.prev and (pos < (self.prev.pos + 2)):
            pos = self.prev.pos + 2
        if self.pos == pos:
            return
        if self.father:
            self.father.set_pos(pos-1)
            if self.father.pos >= pos:
                pos = self.father.pos + 1
        if self.mother:
            self.mother.set_pos(pos+1)
            pos += int((self.mother.pos - pos)/2)
        if pos < 0:
            pos = 0
        self.pos = pos

def build_ancestor_tree(items_tree, indi_id_list, child, indi, level):
    if len(items_tree) < level+1:
        items_tree.append([])
        prev = None
    else:
        prev = items_tree[level][-1]
    ancestor = Ancestor(prev, child, indi)
    items_tree[level].append(ancestor)
    if child:
        if indi.sex == 'M':
            child.father = ancestor
        else:
            child.mother = ancestor
    fam = indi.get_fam()
    if fam:
        if (indi.id not in indi_id_list):
            ancestor.fam_btn = True
        else:
            if fam.husb:
                    build_ancestor_tree(items_tree, indi_id_list, ancestor, fam.husb, level+1)
            if fam.wife:
                    build_ancestor_tree(items_tree, indi_id_list, ancestor, fam.wife, level+1)

def count_ancestor_tree(items_tree, child_pos):
    start_pos = 0
    if (child_pos < 0):
        start_pos = -child_pos
    items_tree[0][0].set_pos(start_pos)
    min_pos = min(items_tree[0][0].pos, child_pos)
    i = 1
    while i < len(items_tree):
        if (min_pos > items_tree[i][0].pos):
            min_pos = items_tree[i][0].pos
        i += 1

