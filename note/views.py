import os
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, HttpResponseNotFound
from django.template import loader
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from hier.utils import get_base_context_ext, process_common_commands, sort_data, extract_get_params
from hier.models import get_app_params
from hier.params import set_sort_mode, toggle_sort_dir, get_search_mode, get_search_info, set_restriction, set_article_kind, set_article_visible
from hier.grp_lst import group_add, group_details, group_toggle, list_add, list_details, build_tree
from hier.categories import get_categories_list
from hier.files import storage_path, get_files_list
from hier.aside import Fix, Sort

from .models import app_name, Note
from .forms import NoteForm, FileForm

from todo.models import Grp, Lst
from todo.utils import nice_date


items_in_page = 10

SORT_MODE_DESCR = {
    '': '',
    'name': _('sort by name'),
    'code': _('sort by code'),
    'descr': _('sort by description'),
    'publ': _('sort by publication date'),
    'last_mod': _('sort by last modification date'),
    'url': _('sort by URL')
}

def get_url_list(app):
    if (app == 'note'):
        return 'note:note_list'
    else:
        return 'news:news_list'

def get_url_form(app):
    if (app == 'note'):
        return 'note:note_form'
    else:
        return 'news:news_form'

#----------------------------------
# Note
#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def item_list(request, app):
    if process_common_commands(request, app): # aside open/close, article open/close
        return HttpResponseRedirect(reverse(get_url_list(app)) + extract_get_params(request))

    if process_sort_commands(request, app):
        return HttpResponseRedirect(reverse(get_url_list(app)) + extract_get_params(request))

    app_param, context = get_base_context_ext(request, app, 'note', _('all').capitalize())

    if (request.method == 'POST'):
        #raise Exception(request.POST)
        if ('item-add' in request.POST):
            item = Note.objects.create(user = request.user, kind = app, name = request.POST['item_add-name'], publ = datetime.now(), lst = app_param.lst)
            return HttpResponseRedirect(reverse(get_url_form(app), args = [item.id]))
        if ('list-add' in request.POST):
            lst_id = list_add(request.user, app, request.POST['name'])
            return HttpResponseRedirect(reverse(app + ':' + app + '_list_form', args = [lst_id]))
        if ('group-add' in request.POST):
            grp_id = group_add(request.user, app, request.POST['name'])
            return HttpResponseRedirect(reverse(app + ':' + app + '_group_form', args = [grp_id]))

    if (app_param.restriction == 'list') and (not app_param.lst):
        if (app == 'note'):
            return HttpResponseRedirect(reverse('note:all_notes'))
        else:
            return HttpResponseRedirect(reverse('news:all_news'))

    fixes = []
    fixes.append(Fix('all', _('all').capitalize(), 'rok/icon/all.png', 'all/', len(Note.objects.filter(user = request.user.id, kind = app))))
    context['fix_list'] = fixes

    sorts = []
    sorts.append(Sort('name',  _('by name').capitalize(), 'todo/icon/sort.png'))
    sorts.append(Sort('descr', _('by description').capitalize(), 'rok/icon/note.png'))
    sorts.append(Sort('publ',  _('by publication date').capitalize(), 'todo/icon/created.png'))
    sorts.append(Sort('lmod',  _('by last modification date').capitalize(), 'todo/icon/planned.png'))
    context['sort_options'] = sorts

    if app_param.sort:
        context['sort_mode'] = SORT_MODE_DESCR[app_param.sort].capitalize()

    if (app == 'note'):
        template_file = 'note/note.html'
        context['add_item_placeholder'] = _('add note').capitalize()
    else:
        template_file = 'note/news.html'
        context['add_item_placeholder'] = _('add news').capitalize()
    
    redirect = False
    if app_param.article:
        if (app_param.kind == 'item'):
            if not Note.objects.filter(id = app_param.art_id, user = request.user.id, kind = app).exists():
                set_article_visible(request.user, app, False)
                redirect = True
            else:
                redirect = item_details(request, context, app_param, app)
        elif (app_param.kind == 'list'):
            can_delete = not Note.objects.filter(lst = app_param.art_id).exists()
            redirect = list_details(request, context, app_param.art_id, app, can_delete)
            if not redirect:
                template_file = 'hier/article_list.html'
        elif (app_param.kind == 'group'):
            redirect = group_details(request, context, app_param.art_id, app)
            if not redirect:
                template_file = 'hier/article_group.html'

    if redirect:
        return HttpResponseRedirect(reverse(get_url_list(app)) + extract_get_params(request))

    tree = build_tree(request.user.id, app)
    for t in tree:
        if t.is_list:
            t.qty = len(Note.objects.filter(user = request.user.id, lst = t.id))
    context['groups'] = tree

    query = None
    if request.method == 'GET':
        query = request.GET.get('q')
    data = filtered_sorted_list(request.user, app_param, query, app)

    page_number = 1
    if (request.method == 'GET'):
        page_number = request.GET.get('page')
    paginator = Paginator(data, items_in_page)
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = paginator.get_page(page_number)
    context['search_info'] = get_search_info(query)
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))


#----------------------------------
def item_form(request, pk, app):
    set_article_kind(request.user, app, 'item', pk)
    return HttpResponseRedirect(reverse(get_url_list(app)) + extract_get_params(request))


#----------------------------------
def all_items(request, app):
    set_restriction(request.user, app, 'all')
    return HttpResponseRedirect(reverse(get_url_list(app)))


#----------------------------------
def list_items(request, pk, app):
    set_restriction(request.user, app, 'list', pk)
    return HttpResponseRedirect(reverse(get_url_list(app)))

#----------------------------------
def list_form(request, pk, app):
    set_article_kind(request.user, app, 'list', pk)
    return HttpResponseRedirect(reverse(get_url_list(app)))

#----------------------------------
def group_form(request, pk, app):
    set_article_kind(request.user, app, 'group', pk)
    return HttpResponseRedirect(reverse(get_url_list(app)))

#----------------------------------
def toggle_group(request, pk, app):
    group_toggle(request.user, app, pk)
    return HttpResponseRedirect(reverse(get_url_list(app)) + extract_get_params(request))

#----------------------------------
def filtered_sorted_list(user, app_param, query, app):
    data = filtered_list(user, app_param.restriction, app, query, app_param.lst)

    if not data:
        return data

    if (app == 'news') and (app_param.sort == ''):
        return data.order_by('-publ')

    return sort_data(data, app_param.sort, app_param.reverse)

#----------------------------------
def filtered_list(user, restriction, app, query = None, lst = None):
    if (restriction == '') or (restriction == 'all'):
        data = Note.objects.filter(user = user.id, kind = app)
    elif (restriction == 'list') and lst:
        data = Note.objects.filter(user = user.id, kind = app, lst = lst.id)
    else:
        data = []

    if not query:
        return data

    search_mode = get_search_mode(query)
    lookups = None
    if (search_mode == 0):
        return data
    elif (search_mode == 1):
        lookups = Q(name__icontains=query) | Q(code__icontains=query) | Q(descr__icontains=query) | Q(url__icontains=query)
    elif (search_mode == 2):
        lookups = Q(categories__icontains=query[1:])
    
    return data.filter(lookups).distinct()

#----------------------------------
def process_sort_commands(request, app):
    if ('sort_delete' in request.POST):
        set_sort_mode(request.user, app, '')
        return True
    if ('sort_name' in request.POST):
        set_sort_mode(request.user, app, 'name')
        return True
    if ('sort_descr' in request.POST):
        set_sort_mode(request.user, app, 'descr')
        return True
    if ('sort_publ' in request.POST):
        set_sort_mode(request.user, app, 'publ')
        return True
    if ('sort_lmod' in request.POST):
        set_sort_mode(request.user, app, 'last_mod')
        return True
    if ('sort_direction' in request.POST):
        toggle_sort_dir(request.user, app)
        return True
    return False

#----------------------------------
def item_details(request, context, app_param, app):
    if not Note.objects.filter(user = request.user.id, kind = app, id = app_param.art_id).exists():
        set_article_visible(request.user, app, False)
        return True

    item = get_object_or_404(Note.objects.filter(user = request.user.id, kind = app, id = app_param.art_id))

    form = None

    if (request.method == 'POST'):
        #raise Exception(request.POST)
        if ('item_delete' in request.POST):
            delete_item(request, app_param.kind, app_param.art_id, app)
            return True
        if ('item_save' in request.POST):
            form = NoteForm(request.user, app, request.POST, instance = item)
            if form.is_valid():
                data = form.save(commit = False)
                data.user = request.user
                if form.cleaned_data.get('category'):
                    if data.categories:
                        data.categories += ' '
                    data.categories += form.cleaned_data['category']
                form.save()
                return True
        if ('url_delete' in request.POST):
            item.url = ''
            item.save()
            return True
        if ('category_delete' in request.POST):
            category = request.POST['category_delete']
            item.categories = item.categories.replace(category, '')
            item.save()
            return True
        if ('file_upload' in request.POST):
            file_form = FileForm(request.POST, request.FILES)
            if file_form.is_valid():
                handle_uploaded_file(request.FILES['upload'], request.user, item, app)
                return True
        if ('file_delete' in request.POST):
            delete_file(request.user, item, request.POST['file_delete'], app)
            return True

    if not form:
        form = NoteForm(request.user, app, instance = item)

    context['form'] = form
    context['ed_item'] = item
    context['categories'] = get_categories_list(item.categories)
    context['files'] = get_files_list(request.user, app, 'note_{}'.format(item.id))
    context['item_info'] = str(_('modificated:').capitalize()) + nice_date(item.last_mod.date())
    return False


#----------------------------------
def delete_item(request, kind, art_id, app):
    if (kind == 'item'):
        item = get_object_or_404(Note.objects.filter(user = request.user.id, id = art_id))
        item.delete()
        set_article_visible(request.user, app, False)


#----------------------------------
def get_file_storage_path(user, item, app):
    return storage_path.format(user.id) + '{}/note_{}/'.format(app, item.id)

#----------------------------------
def handle_uploaded_file(f, user, item, app):
    path = get_file_storage_path(user, item, app)
    os.makedirs(os.path.dirname(path), exist_ok = True)
    with open(path + f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

#----------------------------------
def get_doc(request, name, app):
    app_param = get_app_params(request.user, app)
    item = get_object_or_404(Note.objects.filter(id = app_param.art_id))
    path = get_file_storage_path(request.user, item, app)
    try:
        fsock = open(path + name, 'rb')
        return FileResponse(fsock)
    except IOError:
        response = HttpResponseNotFound()

#----------------------------------
def delete_file(user, item, name, app):
    path = get_file_storage_path(user, item, app)
    os.remove(path + name[4:])

#----------------------------------
def note_list(request):
    return item_list(request, 'note')

def note_form(request, pk):
    return item_form(request, pk, 'note')

def all_notes(request):
    return all_items(request, 'note')

def list_notes(request, pk):
    return list_items(request, pk, 'note')

def note_list_form(request, pk):
    return list_form(request, pk, 'note')

def note_group_form(request, pk):
    return group_form(request, pk, 'note')

def note_toggle_group(request, pk):
    return toggle_group(request, pk, 'note')

def note_get_doc(request, name):
    return get_doc(request, name, 'note')

#----------------------------------
def news_list(request):
    return item_list(request, 'news')

def news_form(request, pk):
    return item_form(request, pk, 'news')

def all_news(request):
    return all_items(request, 'news')

def list_news(request, pk):
    return list_items(request, pk, 'news')

def news_list_form(request, pk):
    return list_form(request, pk, 'news')

def news_group_form(request, pk):
    return group_form(request, pk, 'news')

def news_toggle_group(request, pk):
    return toggle_group(request, pk, 'news')

def news_get_doc(request, name):
    return get_doc(request, name, 'news')


