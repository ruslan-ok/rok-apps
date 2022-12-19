from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
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
def diagram(request):
    ctx = GenealogyContext()
    ctx.request = request
    ctx.set_config(app_config, 'tree')
    ctx.config.set_view(request)
    context = ctx.get_app_context(request.user.id, icon=ctx.config.view_icon)
    template = loader.get_template('family/diagram.html')
    return HttpResponse(template.render(context, request))
