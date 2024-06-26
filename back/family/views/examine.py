import os
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.template import loader
from family.views.base import GenealogyContext
from family.models import FamTreeUser, FamTree
from family.validator.validator import Validator
from task.const import APP_FAMILY


@login_required(login_url='account:login')
def examine_tree(request, pk):
    get_object_or_404(FamTreeUser.objects.filter(user_id=request.user.id, tree_id=pk))
    tree = get_object_or_404(FamTree.objects.filter(id=pk))
    ctx = GenealogyContext()
    ctx.request = request
    ctx.set_config(APP_FAMILY, 'pedigree')
    ctx.config.set_view(request)
    context = ctx.get_app_context(request.user.id, icon=ctx.config.view_icon)
    context['cur_tree_id'] = pk
    context['title'] = f'{_("Examine tree")} {tree.name}'
    template = loader.get_template('family/pedigree/examine.html')
    return HttpResponse(template.render(context, request))

def examine_params(user, item_id) -> tuple[int, str]:
    if FamTreeUser.objects.filter(user_id=user.id, tree_id=item_id, can_view=True).exists():
        if FamTree.objects.filter(id=item_id).exists():
            tree = FamTree.objects.filter(id=item_id).get()
            fname = tree.get_export_file(user)
            validator = Validator(user)
            total = validator.get_tree_file_obj_num(fname)
            return total, ''
    return 0, ''

def examine_start(user, item_id, task_id) -> dict:
    if FamTreeUser.objects.filter(user_id=user.id, tree_id=item_id, can_view=True).exists():
        if FamTree.objects.filter(id=item_id).exists():
            tree = FamTree.objects.filter(id=item_id).get()
            fname = tree.get_export_file(user)
            validator = Validator(user)
            ret = validator.check_tree_file(fname, task_id=task_id)
            return {'status':'completed', 'info': f'GEDCOM version: {ret["gedcom_ver"]}\nFile valid: {ret["file_ok"]}'}
    return {'status':'warning', 'info': f'Family tree with id {task_id} not found'}