from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.shortcuts import get_object_or_404
from rusel.base.context import Context
from family.models import FamTree, Params
from family.config import app_config

class GenealogyContext(Context):
    def get_dataset(self, group, query=None, nav_item=None):
        tree_id = self.request.GET.get('tree')
        if tree_id:
            get_object_or_404(FamTree.objects.filter(id=tree_id))
        return []

    def get_app_context(self, user_id, search_qty=None, icon=None, nav_items=None, role=None, **kwargs):
        self.config.set_view(self.request)
        context = super().get_app_context(user_id, search_qty, icon, nav_items, **kwargs)
        cur_tree = Params.get_cur_tree(self.request.user)
        if cur_tree:
            context['current_group'] = str(cur_tree.id)
        return context

@login_required(login_url='account:login')
def diagram_start(request):
    cur_tree = Params.get_cur_tree(request.user)
    if not cur_tree:
        return HttpResponseRedirect(reverse('family:pedigree-list'))
    cur_indi = Params.get_cur_indi(request.user, cur_tree)
    if not cur_indi:
        return HttpResponseRedirect(reverse('family:pedigree-list'))
    return HttpResponseRedirect(reverse('family:diagram', args=(cur_tree.id,)) + f'#/@I{cur_indi.id}@')

@login_required(login_url='account:login')
def diagram(request, tree_id):
    ctx = GenealogyContext()
    ctx.request = request
    ctx.set_config(app_config, 'tree')
    ctx.config.set_view(request)
    context = ctx.get_app_context(request.user.id, icon=ctx.config.view_icon)
    context['cur_tree_id'] = 1
    context['cur_indi_id'] = '1'
    template = loader.get_template('family/diagram.html')
    return HttpResponse(template.render(context, request))

@login_required(login_url='account:login')
def diagram_debug(request):
    ctx = GenealogyContext()
    ctx.request = request
    ctx.set_config(app_config, 'tree')
    ctx.config.set_view(request)
    context = ctx.get_app_context(request.user.id, icon=ctx.config.view_icon)
    context['cur_tree_id'] = 1
    context['cur_indi_id'] = '1'
    template = loader.get_template('family/diagram_debug.html')
    return HttpResponse(template.render(context, request))
