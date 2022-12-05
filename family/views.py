import urllib, os
from PIL import Image
from dataclasses import dataclass
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404, FileResponse
from django.urls import reverse
from django.template import loader
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from rusel.base.context import Context
from family.config import app_config
from family.models import (FamTree, FamTreeUser, IndividualRecord, FamRecord, MultimediaRecord, Params, IndiInfo, IndiFamilies,
    IndiSpouses)
from family.forms import (CreateFamTreeForm, EditFamTreeForm, CreateIndiForm, CreateFamForm, CreateMediaForm,
    EditIndiEssentials)

class GenealogyContext(Context):
    def get_dataset(self, group, query=None, nav_item=None):
        tree_id = self.request.GET.get('tree')
        if tree_id:
            get_object_or_404(FamTreeUser.objects.filter(user_id=self.request.user.id, tree_id=tree_id))
            if group:
                match group.view_id:
                    case 'pedigree': return FamTreeUser.objects.filter(user_id=self.request.user.id)
                    case 'individual': return IndiInfo.objects.filter(tree_id=tree_id)
                    case 'family': return FamRecord.objects.filter(tree=tree_id)
                    case 'media': return MultimediaRecord.objects.filter(tree=tree_id)
        return []

    def get_app_context(self, user_id, search_qty=None, icon=None, nav_items=None, role=None):
        self.config.set_view(self.request)
        context = super().get_app_context(user_id, search_qty, icon, nav_items)
        cur_tree = Params.get_cur_tree(self.request.user)
        if cur_tree:
            context['current_group'] = str(cur_tree.id)
        context['api_role'] = 'famtree'
        return context

class GenealogyListView(ListView, GenealogyContext, LoginRequiredMixin):

    def __init__(self):
        super().__init__()
        self.set_config(app_config, 'tree')

    def get(self, request):
        if not request.user.is_authenticated:
            raise Http404
        ret = super().get(request)
        cur_tree = Params.get_cur_tree(request.user)
        if (self.config.group_entity not in request.GET and cur_tree):
            return HttpResponseRedirect(request.path + '?' + self.config.group_entity + '=' + str(cur_tree.id))
        elif 'tree' in request.GET:
            s_tree_id = request.GET.get('tree')
            if s_tree_id:
                tree_id = int(s_tree_id)
                if FamTreeUser.objects.filter(user_id=request.user.id, tree_id=tree_id).exists():
                    user_tree = FamTreeUser.objects.filter(user_id=request.user.id, tree_id=tree_id).get()
                    tree = FamTree.objects.filter(id=user_tree.tree_id).get()
                    Params.set_cur_tree(request.user, tree)
        return ret

    def get_context_data(self):
        context = super().get_context_data()
        self.config.set_view(self.request)
        upd_context = self.get_app_context(self.request.user.id, icon=self.config.view_icon)
        context.update(upd_context)
        return context

@dataclass
class Pedigree:
    id: int
    name: str
    important: bool

    def get_absolute_url(self):
        return reverse('family:pedigree-detail', args=(self.id,))

class PedigreeListView(GenealogyListView):
    model = FamTreeUser
    form_class = CreateFamTreeForm
    template_name = 'family/pedigree.html'

    def get_context_data(self):
        context = super().get_context_data()
        return context

    def get_dataset(self, group, nav_item):
        return super().get_dataset(group, nav_item)

    def get_queryset(self):
        ft = FamTreeUser.objects.filter(user_id=self.request.user.id)
        s_tree_id = self.request.GET.get('tree')
        user_tree = None
        if s_tree_id:
            user_tree = get_object_or_404(FamTreeUser.objects.filter(user_id=self.request.user.id, tree_id=int(s_tree_id)))
        ret = []
        for t in ft:
            if t.name:
                important = False
                if user_tree:
                    important = t.tree_id == int(user_tree.tree_id)
                ret.append(Pedigree(id=t.tree_id, name=t.name, important=important))
        return ret

class IndiListView(GenealogyListView):
    model = IndiInfo
    form_class = CreateIndiForm
    template_name = 'family/individuals.html'

    def get_queryset(self):
        tree_id = self.request.GET.get('tree')
        if tree_id:
            get_object_or_404(FamTreeUser.objects.filter(user_id=self.request.user.id, tree_id=tree_id))
            return IndiInfo.objects.filter(tree_id=tree_id)
        return []

class FamListView(GenealogyListView):
    model = FamRecord
    form_class = CreateFamForm
    template_name = 'family/families.html'

    def get_queryset(self):
        tree_id = self.request.GET.get('tree')
        if tree_id:
            get_object_or_404(FamTreeUser.objects.filter(user_id=self.request.user.id, tree_id=tree_id))
            return FamRecord.objects.filter(tree=tree_id)
        return []

class CalendarListView(GenealogyListView):
    model = FamTreeUser
    template_name = 'family/calendar.html'

    def get_queryset(self):
        tree_id = self.request.GET.get('tree')
        if tree_id:
            return FamTreeUser.objects.filter(user_id=self.request.user.id, tree_id=tree_id)
        return []


class NotesListView(GenealogyListView):
    model = FamTreeUser
    template_name = 'family/notes.html'

    def get_queryset(self):
        tree_id = self.request.GET.get('tree')
        if tree_id:
            return FamTreeUser.objects.filter(user_id=self.request.user.id, tree_id=tree_id)
        return []


class MediaListView(GenealogyListView):
    model = MultimediaRecord
    form_class = CreateMediaForm
    template_name = 'family/media.html'

    def get_queryset(self):
        tree_id = self.request.GET.get('tree')
        if tree_id:
            get_object_or_404(FamTreeUser.objects.filter(user_id=self.request.user.id, tree_id=tree_id))
            return MultimediaRecord.objects.filter(tree=tree_id)
        return []


class ReportsListView(GenealogyListView):
    model = FamTreeUser
    template_name = 'family/reports.html'

    def get_queryset(self):
        tree_id = self.request.GET.get('tree')
        if tree_id:
            return FamTreeUser.objects.filter(user_id=self.request.user.id, tree_id=tree_id)
        return []


class GenealogyDetailsView(UpdateView, GenealogyContext, LoginRequiredMixin):

    def __init__(self):
        super().__init__()
        self.set_config(app_config, 'tree')

    def get_context_data(self):
        context = super().get_context_data()
        self.config.set_view(self.request)
        upd_context = self.get_app_context(self.request.user.id, icon=self.config.view_icon)
        context.update(upd_context)
        return context

    def tune_dataset(self, data, group):
        return data

class PedigreeDetailsView(GenealogyDetailsView):
    model = FamTree
    form_class = EditFamTreeForm
    template_name = 'family/famtree-detail.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['sour_corp_addr'] = 'todo::sour_corp_addr'
        context['tree_id'] = self.get_object().id
        return context

EXTRA_FIXES = [
    ('essentials', _('essentials')),
    ('family', _('family')),
    ('biography', _('biography')),
    ('contacts', _('contact info')),
    ('work', _('work')),
    ('education', _('education')),
    ('favorites', _('favorites')),
    ('pers_info', _('personal info')),
    ('citation', _('source citation')),
    ('facts', _('all facts')),
]

class IndiDetailsView(GenealogyDetailsView):
    model = IndiInfo
    form_class = EditIndiEssentials
    template_name = 'family/individual.html'

    def get(self, request, pk):
        if not request.user.is_authenticated:
            raise Http404
        cur_view = None
        if ('view' in self.request.GET):
            cur_view = self.request.GET.get('view')
        extra_fixes_keys = [x[0] for x in EXTRA_FIXES]
        if (cur_view not in extra_fixes_keys):
            return HttpResponseRedirect(reverse('family:individual', args=(self.get_object().id,)) + '?view=essentials')
        self.template_name = 'family/individual/' + cur_view + '.html'
        ret = super().get(request)
        return ret

    def get_context_data(self):
        context = super().get_context_data()
        context['extra_fix_list'] = self.get_extra_fixes()
        context['indi_id'] = self.get_object().id
        cur_view = self.request.GET.get('view')
        match cur_view:
            case 'essentials': pass
            case 'family':
                context['family'] = IndiFamilies.objects.filter(chil_id=self.get_object().id)
                context['spouses'] = self.get_spouses()
            case 'biography': pass
            case 'contacts': pass
            case 'work': pass
            case 'education': pass
            case 'favorites': pass
            case 'pers_info': pass
            case 'citation': pass
            case 'facts': pass
        return context

    def get_spouses(self):
        spouses = IndiSpouses.objects.filter(indi_id=self.get_object().id)
        ret = []
        spouse_id = None
        sp = None
        for spouse in spouses:
            if spouse.spou_id != spouse_id:
                if spouse_id:
                    ret.append(sp)
                spouse_id = spouse.spou_id
                sp = {
                    'id': spouse.spou_id,
                    'givn': spouse.givn,
                    'surn': spouse.surn,
                    'role': '???',
                    'relation': '???',
                    'spou_thumbnail': spouse.spou_thumbnail(),
                    'events': [],
                }
            ev = {
                'date_label': _('date'),
                'date': spouse.date,
                'place_label': _('place'),
                'place': spouse.plac,
                'witnesses_label': _('witnesses'),
                'witnesses': 'spouse.witnesses',
            }
            sp['events'].append(ev)
        if spouse_id:
            ret.append(sp)
        return ret

    def get_extra_fixes(self):
        cur_view = None
        if ('view' in self.request.GET):
            cur_view = self.request.GET.get('view')
        fixes = []
        for fix in EXTRA_FIXES:
            fixes.append({
                'determinator': 'view',
                'id': fix[0],
                'url': reverse('family:individual', args=(self.get_object().id,)) + '?view=' + fix[0],
                'title': _(fix[1]).capitalize(),
                'active': (cur_view == fix[0]),
            })
        return fixes

class FamDetailsView(GenealogyDetailsView):
    model = FamRecord
    form_class = CreateFamForm
    template_name = 'family/family.html'


@login_required(login_url='account:login')
def tree(request):
    tree = None
    indi = None
    if ('indi' not in request.GET and 'tree' not in request.GET):
        tree = Params.get_cur_tree(request.user)
        if tree:
            indi = Params.get_cur_indi(request.user, tree)
        if indi:
            return HttpResponseRedirect(request.path + '?indi=' + str(indi.id))
        if tree:
            return HttpResponseRedirect(request.path + '?tree=' + str(tree.id))
    if ('indi' not in request.GET and 'tree' in request.GET):
        tree_id = request.GET['tree']
        if FamTreeUser.objects.filter(user_id=request.user.id, tree_id=tree_id).exists():
            tree = FamTreeUser.objects.filter(user_id=request.user.id, tree_id=tree_id).get()
        else:
            tree = Params.get_cur_tree(request.user)
        if tree:
            indi = Params.get_cur_indi(request.user, tree)
            if indi:
                return HttpResponseRedirect(request.path + '?indi=' + str(indi.id))
            else:
                return HttpResponseRedirect(reverse('family:individuals') + '?tree=' + str(tree_id))
    indi_list = []
    path_list = []
    indi_ids = None
    if ('indi' in request.GET):
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
    tree_id = None
    if indi:
        tree_id = indi.tree.id
    elif tree:
        tree_id = tree.id
    tree_href = ''
    if tree_id:
        tree_href = '?tree=' + str(tree_id)

    action_list = []
    action_list.append({'name': _('menu').capitalize(), 'w': 100, 'h': 30, 'x': 10, 'y': 10, 'tx': 5, 'ty': 20, 'href': reverse('family:pedigree') + tree_href})
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
    template = loader.get_template('family/famtree-chart.html')
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

#-----------------------------------------------------------------------------

def photo(request, pk):
    file = get_name_from_request(request, 'file')
    user_tree = get_object_or_404(FamTreeUser.objects.filter(user_id=request.user.id, tree_id=pk))
    tree = get_object_or_404(FamTree.objects.filter(id=user_tree.tree_id))
    storage_path = os.environ.get('DJANGO_STORAGE_PATH')
    media_path = storage_path.format('family_tree') + tree.store_name()
    fsock = open(media_path + '/' + file, 'rb')
    return FileResponse(fsock)

def scaled_image(mmr: MultimediaRecord, size: int) -> HttpResponse:
    file = mmr.get_file()
    storage_path = os.environ.get('DJANGO_STORAGE_PATH')
    media_path = storage_path.format('family_tree') + mmr.tree.store_name()
    img = Image.open(media_path + '/' + file)
    if mmr._posi:
        box = tuple([int(x) for x in mmr._posi.split(' ')])
        img = img.crop(box)
    thumb_size = (size, size, )
    img.thumbnail(thumb_size)
    format = mmr.get_format()
    response = HttpResponse(content_type='image/' + format)
    img.save(response, format)
    return response

def thumbnail(request, pk, size=44):
    user_tree = get_object_or_404(FamTreeUser.objects.filter(user_id=request.user.id, tree_id=pk))
    tree = get_object_or_404(FamTree.objects.filter(id=user_tree.tree_id))
    mmr_id = get_name_from_request(request, 'mmr')
    mmr = get_object_or_404(MultimediaRecord.objects.filter(id=mmr_id, tree=tree.id))
    return scaled_image(mmr, size)

def thumbnail_100(request, pk):
    return thumbnail(request, pk, 100)

def get_name_from_request(request, param='file'):
    query = ''
    if (request.method == 'GET'):
        query = request.GET.get(param)
    if not query:
        return ''
    return urllib.parse.unquote_plus(query)

@login_required(login_url='account:login')
def avatar(request, pk):
    indi = get_object_or_404(IndividualRecord.objects.filter(id=pk))
    mmr = indi.get_avatar_mmr()
    return scaled_image(mmr, 150)


