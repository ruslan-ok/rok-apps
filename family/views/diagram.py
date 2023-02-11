from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from family.views.base import GenealogyContext
from family.models import Params, UserSettings
from family.config import app_config


@login_required(login_url='account:login')
def diagram_start(request):
    cur_tree = Params.get_cur_tree(request.user)
    if not cur_tree:
        return HttpResponseRedirect(reverse('family:pedigree-list'))
    cur_indi = UserSettings.get_sel_indi(request.user, cur_tree)
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
    tree = Params.get_cur_tree(request.user)
    indi = UserSettings.get_sel_indi(request.user, tree)
    context['cur_tree_id'] = tree.id if tree else None
    context['cur_indi_id'] = indi.id if indi else None
    template = loader.get_template('family/diagram.html')
    return HttpResponse(template.render(context, request))
