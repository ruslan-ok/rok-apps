import os
from dataclasses import dataclass
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template import loader
from django.http import HttpResponse, FileResponse, HttpResponseNotFound
from django.utils.translation import gettext_lazy as _
from family.views.base import GenealogyListView, GenealogyDetailsView, UploadGedcomView, GenealogyContext
from family.forms import CreateFamTreeForm, EditFamTreeForm
from family.models import FamTree, FamTreeUser, Params, IndividualRecord, FamRecord
from family.config import app_config

@dataclass
class Pedigree:
    id: int
    name: str
    important: bool
    mod_date: str
    num_indi: int
    num_fam: int

    def get_absolute_url(self):
        return reverse('family:pedigree-detail', args=(self.id,))

    def get_custom_attr(self):
        return [{'text': self.mod_date}, {'text': f'{self.num_indi} Individuals'}, {'text': f'{self.num_fam} Families'}]


class PedigreeListView(GenealogyListView):
    model = FamTreeUser
    form_class = CreateFamTreeForm
    template_name = 'family/pedigree/list.html'

    def get_queryset(self):
        ft = FamTreeUser.objects.filter(user_id=self.request.user.id, can_view=True)
        user_tree = Params.get_cur_tree(self.request.user)
        ret = []
        for t in ft:
            if t.name or t.file:
                tree_name = t.name if t.name else t.file
                important = False
                if user_tree:
                    important = t.tree_id == int(user_tree.id)
                num_indi = len(IndividualRecord.objects.filter(tree=t.tree_id))
                num_fam = len(FamRecord.objects.filter(tree=t.tree_id))
                ret.append(Pedigree(id=t.tree_id, name=tree_name, important=important, mod_date=t.last_mod.strftime('%d.%m.%Y'), num_indi=num_indi, num_fam=num_fam))
        return ret

    def get_context_data(self):
        context = super().get_context_data()
        context['add_item_template'] = 'base/add_item_upload.html'
        context['add_item_placeholder'] = f'{_("Upload GEDCOM-file")}'
        context['api_role'] = 'famtree'
        return context

    def post(self, request):
        return UploadGedcomView.as_view()(request) 

class PedigreeDetailsView(GenealogyDetailsView):
    model = FamTree
    form_class = EditFamTreeForm
    template_name = 'family/pedigree/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sour_corp_addr'] = 'todo::sour_corp_addr'
        tree = self.get_object()
        context['tree_id'] = tree.id
        if tree.name:
            name = tree.name
        elif tree.file:
            name = tree.file
        elif tree.sour_name:
            name = tree.sour_name
        else:
            name = f'Family Tree ID={tree.id}'

        context['pedigree_name'] = name
        context['pedigree_source'] = tree.sour_name
        context['pedigree_info'] = f'GEDCOM {tree.gedc_vers}'
        context['pedigree_extra'] = _('Extra fields')
        context['add_item_template'] = 'base/add_item_upload.html'
        context['add_item_placeholder'] = '{}'.format(_('Upload GEDCOM-file'))
        return context

@login_required(login_url='account:login')
def import_tree(request):
    ctx = GenealogyContext()
    ctx.request = request
    ctx.set_config(app_config, 'pedigree')
    ctx.config.set_view(request)
    context = ctx.get_app_context(request.user.id, icon=ctx.config.view_icon)
    context['title'] = f'{_("Import tree")}'
    template = loader.get_template('family/pedigree/import.html')
    return HttpResponse(template.render(context, request))

@login_required(login_url='account:login')
def export_tree(request, pk):
    get_object_or_404(FamTreeUser.objects.filter(user_id=request.user.id, tree_id=pk))
    tree = get_object_or_404(FamTree.objects.filter(id=pk))
    ctx = GenealogyContext()
    ctx.request = request
    ctx.set_config(app_config, 'pedigree')
    ctx.config.set_view(request)
    context = ctx.get_app_context(request.user.id, icon=ctx.config.view_icon)
    context['cur_tree_id'] = pk
    context['title'] = f'{_("Export tree")} "{tree.name}"'
    template = loader.get_template('family/pedigree/export.html')
    return HttpResponse(template.render(context, request))

@login_required(login_url='account:login')
def get_gedcom_file(request, pk):
    tree = get_object_or_404(FamTree.objects.filter(id=pk))
    fpath = tree.get_export_file(request.user)
    if fpath:
        with open(fpath, 'r', encoding='utf-8') as f:
            fname = fpath.split('\\')[-1]
            response = HttpResponse(f, content_type='application/text charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="{fname}"'
            return response
    return HttpResponse('File not found')

def get_doc(request, role, pk, fname):
    if role != 'pedigree':
        return HttpResponseNotFound()
    get_object_or_404(FamTreeUser.objects.filter(user_id=request.user.id, tree_id=pk))
    tree = get_object_or_404(FamTree.objects.filter(id=pk))
    path = os.environ.get('DJANGO_MEDIA_ROOT', '') + f'\\family\\pedigree\\{tree.file}_media\\'
    try:
        fsock = open(path + fname, 'rb')
        return FileResponse(fsock)
    except IOError:
        return HttpResponseNotFound()

