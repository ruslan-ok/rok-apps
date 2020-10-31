import os, urllib.parse
from PIL import Image, UnidentifiedImageError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, HttpResponseNotFound
from django.urls import reverse
from django.utils.encoding import escape_uri_path
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404

from hier.aside import Fix
from hier.utils import get_base_context_ext, process_common_commands, extract_get_params
from hier.params import get_search_info, get_search_mode, set_article_kind, set_article_visible, set_restriction
from hier.files import file_storage_path
from hier.models import get_app_params

from .models import app_name, Photo
from .forms import PhotoForm

items_per_page = 12

#----------------------------------
def all(request):
    set_restriction(request.user, app_name, '')
    set_article_kind(request.user, app_name, '')
    set_article_visible(request.user, app_name, False)
    return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))

#----------------------------------
def map(request):
    set_restriction(request.user, app_name, 'map')
    set_article_kind(request.user, app_name, '')
    set_article_visible(request.user, app_name, False)
    return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))

#----------------------------------
def show(request):
    return show_or_edit(request, False)

#----------------------------------
def edit(request):
    return show_or_edit(request, True)

#----------------------------------
def goto(request):
    set_article_kind(request.user, app_name, '')
    set_article_visible(request.user, app_name, False)
    app_param = get_app_params(request.user, app_name)
    query = ''
    prefix = ''
    if app_param.restriction:
        prefix = app_param.restriction + '/'
    if (request.method == 'GET'):
        query = request.GET.get('file')
    if query:
        set_restriction(request.user, app_name, prefix + query)
    return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))

#----------------------------------
def jump(request, level):
    set_article_kind(request.user, app_name, '')
    set_article_visible(request.user, app_name, False)
    if not level:
        set_restriction(request.user, app_name, '')
    else:
        app_param = get_app_params(request.user, app_name)
        crumbs = app_param.restriction.split('/')
        new_rest = ''
        cur_level = 1
        for crumb in crumbs:
            new_rest += crumb
            if (cur_level < level):
                new_rest += '/'
                cur_level += 1
            else:
                break
        set_restriction(request.user, app_name, new_rest)

    return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def main(request):
    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))

    app_param, context = get_base_context_ext(request, app_name, 'main', _('photos'))

    redirect = False

    if (app_param.kind == 'photo'):
        valid_article = Photo.objects.filter(id = app_param.art_id, user = request.user.id).exists()
        if not valid_article:
            set_article_kind(request.user, app_name, '')
            set_article_visible(request.user, app_name, False)
            redirect = True
        else:
            item = get_object_or_404(Photo.objects.filter(id = app_param.art_id, user = request.user.id))
            path = get_file_storage_path(request.user)
            orient = get_img_orient(path + item.full_name())
            context['item'] = { 'show_url': 'show/?file=' + item.full_name(), 'edit_url': 'edit/?file=' + item.full_name(), 'orient': orient, 'alt': item.name, 'info': item.name }
            context['title'] = item.name
            if app_param.article:
                redirect = edit_item(request, context, item, False)
    
    if redirect:
        return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))

    query = None
    page_number = 1
    if (request.method == 'GET'):
        query = request.GET.get('q')
        page_number = request.GET.get('page')
    context['search_info'] = get_search_info(query)
    context['hide_add_item_input'] = True

    data = filtered_sorted_list(request.user, app_param, query)

    fixes = []
    fixes.append(Fix('', _('all').capitalize(), 'rok/icon/all.png', 'all/', len(data)))
    fixes.append(Fix('map', _('on the map').capitalize(), 'todo/icon/map.png', 'map/', len(data)))
    context['fix_list'] = fixes

    bread_crumbs = []
    crumbs = app_param.restriction.split('/')
    if ((len(crumbs) > 0) and crumbs[0]) or (app_param.kind == 'photo'):
        bread_crumbs.append({ 'url': 'level/0/', 'name': '[ / ]' })

    level = 1
    for crumb in crumbs:
        if not crumb:
            continue
        if (level == len(crumbs)) and (app_param.kind == ''):
            context['title'] = crumb
        else:
            url = 'level/{}/'.format(level)
            bread_crumbs.append({ 'url': url, 'name': crumb })
        level += 1
    context['bread_crumbs'] = bread_crumbs

    paginator = Paginator(data, items_per_page)
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = paginator.get_page(page_number)
    if (app_param.kind == 'photo'):
        template_name = 'photo/photo.html'
    else:
        template_name = 'photo/list.html'
    template = loader.get_template(template_name)
    return HttpResponse(template.render(context, request))


def filtered_sorted_list(user, app_param, query):
    data = filtered_list(user, app_param.restriction, query)
    return data

def get_file_storage_path(user):
    return file_storage_path.format(user.id) + 'photo/'

def filtered_list(user, restriction, query = None):
    data = []
    path = get_file_storage_path(user)
    path_len = len(path)
    for dirname, subdirs, files in os.walk(path + restriction):
        subdir = ''
        if (len(dirname) > path_len):
            subdir = dirname[path_len:] + '/'
        
        for f in subdirs:
            img_obj = { 'show_url': 'show/?file=dir', 'edit_url': 'goto/?file=' + urllib.parse.quote_plus(f), 'orient': 'h', 'alt': f, 'info': f }
            data.append(img_obj)
    
        for f in files:
            if (f == 'Thumbs.db'):
                continue
            orient = get_img_orient(dirname + '/' + f)
            photo = urllib.parse.quote_plus(subdir + f)
            img_obj = { 'show_url': 'show/?file=' + photo, 'edit_url': 'edit/?file=' + photo, 'orient': orient, 'alt': f, 'info': f }
            data.append(img_obj)
        break
    return data

#----------------------------------
def get_img_orient(file_path):
    orient = 'h'
    try:
        im = Image.open(file_path)
        if (not im._getexif()) or (im._getexif().get(274,0) < 5): # EXIF rotation information
            width, height = im.size
        else:
            height, width = im.size
        if (width < height):
            orient = 'v'
    except UnidentifiedImageError:
        pass
    except FileNotFoundError:
        pass
    return orient

#----------------------------------
def show_or_edit(request, do_edit):
    path = get_file_storage_path(request.user)
    query = ''
    if (request.method == 'GET'):
        query = request.GET.get('file')
    if not query:
        return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))
    name = urllib.parse.unquote_plus(query)
    if (name == 'dir'):
        path = 'C:/Web/apps/rusel/static/rok/icon/'
        name = 'folder.png'
    try:
        fsock = open(path + name, 'rb')
        if not do_edit:
            return FileResponse(fsock)
        dirs = name.split('/')
        sub_name = dirs[-1:][0]
        if (len(dirs) > 1):
            sub_path = name[:len(name)-len(sub_name)-1]
        else:
            sub_path = ''
        if Photo.objects.filter(name = sub_name, path = sub_path, user = request.user.id).exists():
            pk = Photo.objects.filter(name = sub_name, path = sub_path, user = request.user.id).get().id
        else:
            pk = Photo.objects.create(name = sub_name, path = sub_path, user = request.user).id
        set_article_kind(request.user, app_name, 'photo', pk)
        return HttpResponseRedirect(reverse('photo:main') + extract_get_params(request))
    except IOError:
        return HttpResponseNotFound()

#----------------------------------
def edit_item(request, context, item, disable_delete = False):
    form = None
    if (request.method == 'POST'):
        if ('article_delete' in request.POST):
            delete_item(request, item, disable_delete)
            return True
        if ('item-save' in request.POST):
            form = PhotoForm(request.POST, instance = item)
            if form.is_valid():
                data = form.save(commit = False)
                data.user = request.user
                form.save()
                return True

    if not form:
        form = PhotoForm(instance = item)

    context['form'] = form
    context['ed_item'] = item
    return False

#----------------------------------
def delete_item(request, item, disable_delete = False):
    if disable_delete:
        return False
    item.delete()
    set_article_kind(request.user, app_name, '')
    set_article_visible(request.user, app_name, False)
    return True

