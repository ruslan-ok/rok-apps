import sys
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import loader
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.translation import gettext_lazy as _

from .models import Folder
from .forms import FolderForm
from .utils import rmtree, get_base_context, save_folder_id, is_in_trash, put_in_the_trash, process_common_commands

errors = []

app_name = 'hier'

#----------------------------------
def not_hier_app(folder):
    if (folder.model_name[:6] == 'apart:') or (folder.model_name[:5] == 'fuel:') or (folder.model_name[:5] == 'proj:') or \
       (folder.model_name[:5] == 'trip:') or (folder.model_name[:5] == 'wage:') or (folder.model_name[:5] == 'todo:'):
        return True
    return False

#----------------------------------
def hier_app(folder):
    return not not_hier_app(folder)

#----------------------------------
def folder_param(request, folder_id):
    folder = get_object_or_404(Folder.objects.filter(id = folder_id, user = request.user.id))
    if folder.model_name:
        try:
            url = reverse(folder.model_name + '_param', args = [folder_id])
            return HttpResponseRedirect(url)
        except NoReverseMatch:
            pass
        else:
            raise Exception(sys.exc_info()[0])
    return _folder_list(request, folder_id, False)

def can_del(folder):
    if (folder.content_id == 0) or (folder.model_name == ''):
        if Folder.objects.filter(node = folder.id).exists():
            errors.append('Папка без контента не пустая, поэтому не может быть удалена')
        else:
            return True
    else:
        if Folder.objects.filter(content_id = folder.content_id, model_name = folder.model_name).exclude(id = folder.id).exists():
            # Существует ещё одна другая папка, ассоциированная с этим же контентом. Значит эту можно удалить.
            return True
        else:
            errors.append('Для удаления папки с контентом следует удалить контент')
    return False

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def show_page_list(request, folder_id, title, name, data, extra_context = {}):
    context = get_base_context(request, folder_id, 0, title, 'dir')
    context[name + 's'] = data
    context.update(extra_context)
    template = loader.get_template('hier/' + name + '_list.html')
    return HttpResponse(template.render(context, request))

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def show_page_form(request, node_id, folder_id, title, name, form, extra_context = {}):
    if (request.method == 'POST'):
        if form.is_valid():
            data = form.save(commit = False)
            data.user = request.user
            data.node = node_id
            last_mod = datetime.now()
            if (folder_id == 0):
                creation = datetime.now()
            form.save()
            folder_id = data.id
            return HttpResponseRedirect(reverse('hier:' + name + '_list', args = [folder_id]))
    context = get_base_context(request, folder_id, 0, title, 'folder', form = form)
    context['pk'] = folder_id
    context.update(extra_context)
    template = loader.get_template('hier/' + name + '_form.html')
    return HttpResponse(template.render(context, request))
