from ast import Param
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from rusel.base.context import Context
from genea.config import app_config
from genea.models import FamTree, IndividualRecord, FamRecord, ChildToFamilyLink, Params

class TreeContext(Context):
    def get_dataset(self, group, query=None, nav_item=None):
        return []

def no_data(request):
    ctx = TreeContext()
    ctx.request = request
    ctx.set_config(app_config, 'tree')
    ctx.config.set_view(request)
    context = ctx.get_app_context(request.user.id)
    template = loader.get_template('genea/no_data.html')
    return HttpResponse(template.render(context, request))

def refresh(request):
    tree, indi = get_tree_indi(request)
    if not tree or not indi:
        return HttpResponseRedirect(reverse('genea:no_data'))
    s_depth = request.GET.get('depth')
    try:
        depth = int(s_depth)
    except (TypeError, ValueError):
        depth = None
    if not depth:
        depth = tree.depth
    if not depth or depth < 1 or depth > 5:
        depth = 2
    if tree.depth != depth:
        tree.depth = depth
        tree.save()
    return HttpResponseRedirect(reverse('genea:list') + '?tree=' + str(tree.id) + '&indi=' + str(indi.id) + '&depth=' + str(depth))

def do_refresh(request):
    params = ''
    if request.GET:
        params = '?' + request.GET.urlencode()
    return HttpResponseRedirect(reverse('genea:refresh') + params)

def pedigree(request):
    if ('tree' not in request.GET) or ('indi' not in request.GET) or ('depth' not in request.GET):
        return do_refresh(request)
    s_depth = request.GET.get('depth')
    try:
        depth = int(s_depth)
    except ValueError:
        return do_refresh(request)
    if (depth < 1) or (depth > 5):
        return do_refresh(request)
    tree_id = request.GET.get('tree')
    tree = None
    if FamTree.objects.filter(id=tree_id).exists():
        tree = FamTree.objects.filter(id=tree_id).get()
    if not tree:
        return do_refresh(request)
    indi = None
    indi_id = request.GET.get('indi')
    if IndividualRecord.objects.filter(tree=tree_id, id=indi_id).exists():
        indi = IndividualRecord.objects.filter(tree=tree_id, id=indi_id).get()
    if not indi:
        return do_refresh(request)
    if tree.depth != depth:
        tree.depth = depth
        tree.save()
    ctx = TreeContext()
    ctx.request = request
    ctx.set_config(app_config, 'tree')
    ctx.config.set_view(request)
    context = ctx.get_app_context(request.user.id)
    context['tree_list'] = get_tree_list()
    context['cur_tree'] = tree
    context['cur_indi'] = indi
    context['cur_depth'] = depth
    context['indi_list'] = get_indi_list(tree)
    ftv = FamTreeView(depth)
    ftv.build_tree(indi)
    context['tree_levels'] = ftv.levels
    template = loader.get_template('genea/tree.html')
    return HttpResponse(template.render(context, request))

def get_tree_indi(request):
    tree = None
    indi = None
    if 'indi' in request.GET:
        indi_id = int(request.GET.get('indi'))
        if IndividualRecord.objects.filter(id=indi_id).exists():
            indi = IndividualRecord.objects.filter(id=indi_id).get()
            tree = indi.tree
    if not indi:
        if 'tree' not in request.GET:
            tree = get_cur_tree(request.user.id)
        if not tree and 'tree' in request.GET:
            tree_id = int(request.GET.get('tree'))
            if FamTree.objects.filter(id=tree_id).exists():
                tree = FamTree.objects.filter(id=tree_id).get()
    if not tree and len(FamTree.objects.all()) > 0:
        tree = FamTree.objects.all()[0]
        set_cur_tree(request.user, tree)
    if tree:
        if not indi:
            if tree.cur_indi:
                if IndividualRecord.objects.filter(tree=tree.id, id=tree.cur_indi).exists():
                    indi = IndividualRecord.objects.filter(tree=tree.id, id=tree.cur_indi).get()
            else:
                if IndividualRecord.objects.filter(tree=tree.id).exists():
                    indi = IndividualRecord.objects.filter(tree=tree.id)[0]
        set_cur_indi(tree, indi)

    set_cur_tree(request.user, tree)
    return tree, indi

def get_cur_tree(user_id):
    if Params.objects.filter(user=user_id).exists():
        params = Params.objects.filter(user=user_id).get()
        return params.cur_tree
    return None

def set_cur_tree(user, tree):
    if user and tree:
        if not Params.objects.filter(user=user.id).exists():
            Params.objects.create(user=user, cur_tree=tree)
        else:
            params = Params.objects.filter(user=user.id).get()
            params.cur_tree = tree
            params.save()

def set_cur_indi(tree, indi):
    if tree and indi and tree.cur_indi != indi.id:
        tree.cur_indi = indi.id
        tree.save()

def get_tree_list():
    return FamTree.objects.all()

def get_indi_list(tree):
    return IndividualRecord.objects.filter(tree=tree)

class FamTreeView:
    def __init__(self, max_depth, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.levels = []
        self.cur_indi_level = None
        self.max_depth = max_depth

    def build_tree(self, main):
        if main:
            self.levels.append([])
            self.cur_indi_level = 0
            self.levels[0].append(main)
            self.add_parents(main, -1)
            self.add_spouses(main, self.cur_indi_level, with_parents=True)

    def add_spouses(self, indi, level_num, with_parents=False):
            for fam in FamRecord.objects.filter(husb=indi.id):
                if fam.wife:
                    self.levels[level_num].append(fam.wife)
                    if with_parents:
                        self.add_parents(fam.wife, level_num-1)
                self.add_children(fam, level_num+1)
            for fam in FamRecord.objects.filter(wife=indi.id):
                if fam.husb:
                    self.levels[level_num].append(fam.husb)
                    if with_parents:
                        self.add_parents(fam.husb, level_num-1)
                self.add_children(fam, level_num+1)

    def add_parents(self, indi, level_num):
        if (self.cur_indi_level - level_num) > self.max_depth:
            return
        for child_fam in ChildToFamilyLink.objects.filter(chil=indi.id):
            if child_fam.fami.husb:
                if level_num < 0:
                    level_num += 1
                    self.cur_indi_level += 1
                    self.levels.insert(0, [])
                self.levels[level_num].append(child_fam.fami.husb)
                self.add_parents(child_fam.fami.husb, level_num-1)
            if child_fam.fami.wife:
                if level_num < 0:
                    level_num += 1
                    self.cur_indi_level += 1
                    self.levels.insert(0, [])
                self.levels[level_num].append(child_fam.fami.wife)
                self.add_parents(child_fam.fami.wife, level_num-1)

    def add_children(self, fam, level_num):
        if (level_num - self.cur_indi_level) > self.max_depth:
            return
        for child_fam in ChildToFamilyLink.objects.filter(fami=fam.id):
            if level_num > (len(self.levels)-1):
                self.levels.append([])
            self.levels[level_num].append(child_fam.chil)
            self.add_spouses(child_fam.chil, level_num)

