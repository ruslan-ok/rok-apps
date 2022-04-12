from django.http import HttpResponse
from django.template import loader
from rusel.base.context import Context
from genea.config import app_config
from genea.models import Header, IndividualRecord, FamRecord, ChildToFamilyLink

class TreeContext(Context):
    def get_dataset(self, group, query=None, nav_item=None):
        return []

def pedigree(request):
    ctx = TreeContext()
    ctx.request = request
    ctx.set_config(app_config, 'tree')
    ctx.config.set_view(request)
    context = ctx.get_app_context(request.user.id)
    tree = None
    indi = None
    indi_id = None
    if 'indi' in request.GET:
        indi_id = int(request.GET.get('indi'))
        if IndividualRecord.objects.filter(id=indi_id).exists():
            indi = IndividualRecord.objects.filter(id=indi_id).get()
            tree = indi.head
    if not indi:
        tree_id = None
        if 'tree' in request.GET:
            tree_id = int(request.GET.get('tree'))
            if Header.objects.filter(id=tree_id).exists():
                tree = Header.objects.filter(id=tree_id).get()
                if IndividualRecord.objects.filter(head=tree_id).exists():
                    indi = IndividualRecord.objects.filter(head=tree_id)[0]
    if not indi and len(Header.objects.all()) > 0:
        tree = Header.objects.all()[0]
        if len(IndividualRecord.objects.filter(head=tree.id)) > 0:
            indi = IndividualRecord.objects.filter(head=tree.id)[0]
    context['tree_levels'] = get_tree(tree, indi)
    template = loader.get_template('genea/tree.html')
    return HttpResponse(template.render(context, request))


def get_tree(tree, main):
    level1 = []
    level2 = []
    level3 = []
    if main:
        level2.append(main)
        add_parents(level1, main)
        print(main.name())
        for fam in FamRecord.objects.filter(husb=main.id):
            if fam.wife:
                level2.append(fam.wife)
                add_parents(level1, fam.wife)
            for child_fam in ChildToFamilyLink.objects.filter(fami=fam.id):
                level3.append(child_fam.chil)
        for fam in FamRecord.objects.filter(wife=main.id):
            if fam.husb:
                level2.append(fam.husb)
                add_parents(level1, fam.husb)
            for child_fam in ChildToFamilyLink.objects.filter(fami=fam.id):
                level3.append(child_fam.chil)
    return [level1, level2, level3, ]

def add_parents(level, indi):
    for child_fam in ChildToFamilyLink.objects.filter(chil=indi.id):
        if child_fam.fami.husb:
            level.append(child_fam.fami.husb)
        if child_fam.fami.wife:
            level.append(child_fam.fami.wife)


"""
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rusel.base.views import BaseListView
from task.const import APP_GENEA, ROLE_STEMMA, NUM_ROLE_STEMMA
from genea.models import Header
from genea.config import app_config
from genea.gedcom_551.exp import ExpGedcom551

app = APP_GENEA
role = ROLE_STEMMA

class StemmaListView(BaseListView):
    model = Header

    def __init__(self, *args, **kwargs):
        super().__init__(app_config, role, *args, **kwargs)

    def form_valid(self, form):
        form.instance.app_apart = NUM_ROLE_STEMMA
        response = super().form_valid(form)
        return response

    def get_dataset(self, group, query=None, nav_item=None):
        return Header.objects.all()

    def tune_dataset(self, data, group):
        return Header.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

def chart_family(request):
    return HttpResponse('Chart Family')
    
def chart_ancestors(request):
    return HttpResponse('Chart Ancestors')

def export(request, pk):
    folder = 'C:\\gedcom\\exp'
    mgr = ExpGedcom551(request)
    mgr.export_gedcom_551(folder, pk)
    return HttpResponseRedirect(reverse('genea:list'))
"""
