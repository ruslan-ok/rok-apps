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

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
# Toggle tree node
#----------------------------------
def toggle(request, folder_id):
    node = Folder.objects.filter(id = folder_id).get()
    node.is_open = not node.is_open
    node.save()
    cur_page = request.GET.get('p')
    if cur_page:
        return HttpResponseRedirect(cur_page)
    else:    
        return HttpResponseRedirect(reverse('hier:folder_list', args = [folder_id]))

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
# Folders List
#----------------------------------
def _folder_list(request, folder_id, show_content, query = None):
    process_common_commands(request)
    data = Folder.objects.filter(user = request.user.id, node = folder_id).order_by('code', 'name')
    save_folder_id(request.user, folder_id)

    title = _('folders')
    if folder_id:
        folder = get_object_or_404(Folder.objects.filter(id = folder_id, user = request.user.id))
        if show_content and folder.model_name:
            try:
                args = []
                if hier_app(folder):
                    args.append(folder_id)

                if folder.content_id:
                    args.append(folder.content_id)

                query_tail = ''
                if query:
                    query_tail = '?q=' + query
                    
                url = reverse(folder.model_name, args = args) + query_tail

                return HttpResponseRedirect(url)
            except NoReverseMatch:
                pass
            else:
                raise Exception(sys.exc_info()[0])
        title = folder.name

    return show_page_list(request, folder_id, title, 'folder', data, {'errors': errors})

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

#----------------------------------
def folder_list(request, folder_id):
    query = request.GET.get('q')
    return _folder_list(request, folder_id, True, query)

#----------------------------------
def folder_down(request, folder_id):
    errors.clear()
    folder = get_object_or_404(Folder.objects.filter(id = folder_id, user = request.user.id))
    if folder.node:
        node = get_object_or_404(Folder.objects.filter(id = folder.node, user = request.user.id))
        if not node.is_open:
            node.is_open = True
            node.save()
        if node.node:
            node_up = get_object_or_404(Folder.objects.filter(id = node.node, user = request.user.id))
            if not node_up.is_open:
                node_up.is_open = True
                node_up.save()
    return HttpResponseRedirect(reverse('hier:folder_list', args = [folder_id]))

#----------------------------------
def folder_dir(request, folder_id):
    return _folder_list(request, folder_id, False)

#----------------------------------
def folder_add(request, folder_id):
    if (request.method == 'POST'):
        form = FolderForm(request.POST)
    else:
        initials = {}
        if Folder.objects.filter(user = request.user.id, id = folder_id).exists():
            node = Folder.objects.filter(user = request.user.id, id = folder_id).get()
            initials['icon'] = node.icon
            initials['color'] = node.color
            initials['model_name'] = node.model_name
        form = FolderForm(initial = initials)
    return show_page_form(request, folder_id, 0, _('create a new folder'), 'folder', form)

#----------------------------------
def folder_form(request, folder_id):
    data = get_object_or_404(Folder.objects.filter(id = folder_id, user = request.user.id))
    if (request.method == 'POST'):
        form = FolderForm(request.POST, instance = data)
    else:
        form = FolderForm(instance = data)
    return show_page_form(request, data.node, folder_id, _('folder') + ' "' + data.name + '"', 'folder', form)

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
def folder_del(request, folder_id):
    data = get_object_or_404(Folder.objects.filter(id = folder_id, user = request.user.id))
    errors.clear()
    redirect_id = data.node
    if can_del(data):
        data.delete()
    else:
        if not is_in_trash(folder_id):
            put_in_the_trash(request.user, folder_id)
        else:
            errors.append('Единственная папка для контента и уже находится в корзине')

    return HttpResponseRedirect(reverse('hier:folder_list', args = [redirect_id]))


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def folder_move(request, folder_id, to_folder):
    cur_folder = get_object_or_404(Folder.objects.filter(id = folder_id, user = request.user.id))
    dst_folder = get_object_or_404(Folder.objects.filter(id = to_folder, user = request.user.id))
    cur_folder.node = to_folder
    cur_folder.save()
    return HttpResponseRedirect(reverse('hier:folder_list', args = [to_folder]))



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
