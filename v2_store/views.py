import locale

from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.translation import gettext_lazy as _
from django.template import loader
from django.utils.crypto import get_random_string

from v2_hier.utils import get_base_context_ext, process_common_commands, sort_data, extract_get_params
from v2_hier.params import set_article_visible, set_restriction, set_aside_visible, get_search_mode, get_search_info
from v2_hier.categories import get_categories_list
from v2_hier.grp_lst import group_add, group_details, group_toggle, list_add, list_details, build_tree
from hier.models import Folder, get_app_params
from v2_hier.params import set_sort_mode, toggle_sort_dir, set_article_kind
from v2_hier.aside import Fix, Sort
from todo.models import Grp, Lst
from v2_todo.utils import nice_date
from store.models import app_name, Entry, Params
from .forms import EntryForm, ParamsForm

url_list = 'v2_store:entry_list'
url_form = 'v2_store:entry_form'
url_param = 'v2_store:param_list'
template_entry = 'v2_store/entries.html'
template_param = 'v2_store/params.html'
items_in_page = 10

SORT_MODE_DESCR = {
    '': '',
    'title': _('sort by title'),
    'username': _('sort by username'),
    'url': _('sort by URL'),
    'created': _('sort by create date')
}


def entry_list(request):
    return do_entry_list(request)

def entry_form(request, pk):
    set_article_kind(request.user, app_name, 'item', pk)
    return HttpResponseRedirect(reverse(url_list) + extract_get_params(request))

def actual(request):
    set_restriction(request.user, app_name, 'actual')
    return HttpResponseRedirect(reverse(url_list))

def waste(request):
    set_restriction(request.user, app_name, 'waste')
    return HttpResponseRedirect(reverse(url_list))

def all(request):
    set_restriction(request.user, app_name, 'all')
    return HttpResponseRedirect(reverse(url_list))

def params(request):
    set_restriction(request.user, app_name, 'default')
    return HttpResponseRedirect(reverse(url_list))

def list_items(request, pk):
    set_restriction(request.user, app_name, 'list', pk)
    return HttpResponseRedirect(reverse(url_list))

def list_form(request, pk):
    set_article_kind(request.user, app_name, 'list', pk)
    return HttpResponseRedirect(reverse(url_list))

def group_form(request, pk):
    set_article_kind(request.user, app_name, 'group', pk)
    return HttpResponseRedirect(reverse(url_list))

def toggle_group(request, pk):
    group_toggle(request.user, app_name, pk)
    return HttpResponseRedirect(reverse(url_list) + extract_get_params(request))

def store_entity(request, name, pk):
    set_restriction(request.user, app_name, 'all')
    if (name == 'group'):
        return group_form(request, pk)
    elif (name == 'list'):
        return list_form(request, pk)
    else:
        set_article_kind(request.user, app_name, 'item', pk)
        return HttpResponseRedirect(reverse('v2_store:all'))

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def do_entry_list(request):
    locale.setlocale(locale.LC_CTYPE, request.LANGUAGE_CODE)
    locale.setlocale(locale.LC_TIME, request.LANGUAGE_CODE)

    if process_common_commands(request, app_name): # aside open/close, article open/close
        return HttpResponseRedirect(reverse(url_list) + extract_get_params(request))

    if process_sort_commands(request):
        return HttpResponseRedirect(reverse(url_list) + extract_get_params(request))

    app_param = get_app_params(request.user, app_name)
    store_params = get_store_params(request.user)

    form = None
    if (request.method == 'POST'):
        #raise Exception(request.POST)
        if ('item-add' in request.POST):
            item = Entry.objects.create(user = request.user, title = request.POST['item_add-name'], value = make_random_string(request.user), lst = app_param.lst)
            return HttpResponseRedirect(reverse(url_form, args = [item.id]))
        if ('param-save' in request.POST):
            form = ParamsForm(request.POST, instance = store_params)
            if form.is_valid():
                data = form.save(commit = False)
                data.user = request.user
                form.save()
                return HttpResponseRedirect(reverse(url_param))
        if ('list-add' in request.POST):
            lst_id = list_add(request.user, app_name, request.POST['name'])
            return HttpResponseRedirect(reverse('v2_store:list_form', args = [lst_id]))
        if ('group-add' in request.POST):
            grp_id = group_add(request.user, app_name, request.POST['name'])
            return HttpResponseRedirect(reverse('v2_store:group_form', args = [grp_id]))

    entity = 'entry'
    article_enabled = True
    template_file = template_entry

    if (app_param.restriction == 'default'):
        entity = 'param'
        article_enabled = False
        template_file = template_param
        if not form:
            form = ParamsForm(instance = store_params)
    elif (app_param.restriction == 'list') and (not app_param.lst):
        return HttpResponseRedirect(reverse('v2_store:all'))

    title = get_title(app_param.restriction)
    app_param, context = get_store_base_context(request, entity, title, article_enabled)

    sorts = []
    sorts.append(Sort('title', _('by title').capitalize(), 'v2/todo/icon/important.png'))
    sorts.append(Sort('user', _('by user name').capitalize(), 'v2/todo/icon/planned.png'))
    sorts.append(Sort('url', _('by URL').capitalize(), 'v2/todo/icon/myday.png'))
    sorts.append(Sort('created', _('by creation date').capitalize(), 'v2/todo/icon/created.png'))
    context['sort_options'] = sorts

    context['add_item_placeholder'] = _('add entry').capitalize()

    if app_param.sort:
        context['sort_mode'] = SORT_MODE_DESCR[app_param.sort].capitalize()

    if (app_param.restriction == 'default'):
        if type(title) is tuple:
            context['form_title'] = _(title[0]).capitalize()
        else:
            context['form_title'] = _(title).capitalize()
        context['form'] = form

    redirect = False
    if app_param.article:
        if (app_param.restriction == 'default'):
            set_article_visible(request.user, app_name, False)
            redirect = True
        elif (app_param.kind == 'item'):
            if not Entry.objects.filter(id = app_param.art_id, user = request.user.id).exists():
                set_article_visible(request.user, app_name, False)
                redirect = True
            else:
                redirect = get_article_item(request, context, app_param)
        elif (app_param.kind == 'list'):
            can_delete = not Entry.objects.filter(lst = app_param.art_id).exists()
            redirect = list_details(request, context, app_param.art_id, app_name, can_delete)
            if not redirect:
                template_file = 'hier/article_list.html'
        elif (app_param.kind == 'group'):
            redirect = group_details(request, context, app_param.art_id, app_name)
            if not redirect:
                template_file = 'hier/article_group.html'

    if redirect:
        return HttpResponseRedirect(reverse(url_list) + extract_get_params(request))

    query = None
    if request.method == 'GET':
        query = request.GET.get('q')
    data = filtered_sorted_list(request.user, app_param, query)

    page_number = 1
    if (request.method == 'GET'):
        page_number = request.GET.get('page')
    paginator = Paginator(data, items_in_page)
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = paginator.get_page(page_number)
    context['search_info'] = get_search_info(query)
    context['search_qty'] = len(data)
    context['search_data'] = query and (len(data) > 0)
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))


#----------------------------------
PAGES = {
    'all': 'all entries',
    'actual': 'actual entries',
    'waste': 'waste entries',
    'default': 'default parameters'
    }
#----------------------------------
def get_title(restriction):
    if (restriction == 'list'):
        return 'list', ''
    return PAGES[restriction], ''


#----------------------------------
def get_store_base_context(request, entity, title, article_enabled):
    app_param, context = get_base_context_ext(request, app_name, entity, title, article_enabled = article_enabled)

    fixes = []
    fixes.append(Fix('actual', _('actual').capitalize(), 'v2/todo/icon/myday.png', 'actual/', len(filtered_list(request.user, 'actual'))))
    fixes.append(Fix('waste', _('waste').capitalize(), 'v2/todo/icon/completed.png', 'waste/', len(filtered_list(request.user, 'waste'))))
    fixes.append(Fix('all', _('all').capitalize(), 'v2/rok/icon/all.png', 'all/', len(filtered_list(request.user, 'all'))))
    fixes.append(Fix('default', _('default options').capitalize(), 'v2/rok/icon/param.png', 'params/', None))
    context['fix_list'] = fixes

    tree = build_tree(request.user.id, app_name)
    for t in tree:
        if t.is_list:
            t.qty = len(Entry.objects.filter(user = request.user.id, lst = t.id))
    context['groups'] = tree

    return app_param, context


#----------------------------------
def filtered_sorted_list(user, app_param, query):
    data = filtered_list(user, app_param.restriction, query, app_param.lst)

    if not data:
        return data

    return sort_data(data, app_param.sort, app_param.reverse)


def filtered_list(user, restriction, query = None, lst = None):
    if (restriction == 'all'):
        data = Entry.objects.filter(user = user.id)
    elif (restriction == 'waste'):
        data = Entry.objects.filter(user = user.id).exclude(actual = 1)
    elif (restriction == 'actual'):
        data = Entry.objects.filter(user = user.id, actual = 1)
    elif (restriction == 'list') and lst:
        data = Entry.objects.filter(user = user.id, lst = lst.id)
    else:
        data = []

    if not query:
        return data

    search_mode = get_search_mode(query)
    lookups = None
    if (search_mode == 0):
        return data
    elif (search_mode == 1):
        lookups = Q(title__icontains=query) | Q(username__icontains=query) | Q(url__icontains=query) | Q(notes__icontains=query)
    elif (search_mode == 2):
        lookups = Q(categories__icontains=query[1:])

    return data.filter(lookups).distinct()

def get_article_item(request, context, app_param):
    if not Entry.objects.filter(user = request.user.id, id = app_param.art_id).exists():
        set_article_visible(request.user, app_name, False)
        return True

    item = get_object_or_404(Entry.objects.filter(user = request.user.id, id = app_param.art_id))

    form = None

    if (request.method == 'POST'):
        #raise Exception(request.POST)
        if ('item_delete' in request.POST):
            item_delete(request, app_param.kind, app_param.art_id)
            return True
        if ('item_save' in request.POST):
            form = EntryForm(request.user, request.POST, instance = item)
            if form.is_valid():
                data = form.save(commit = False)
                data.user = request.user
                if form.cleaned_data['category']:
                    if data.categories:
                        data.categories += ' '
                    data.categories += form.cleaned_data['category']
                form.save()
                return True
        if ('set-actual' in request.POST):
            item.actual = not item.actual
            item.save()
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

    if not form:
        form = EntryForm(request.user, instance = item)

    context['form'] = form
    context['article_id'] = item.id
    context['url_cutted'] = item.url
    if (len(item.url) > 50):
        context['url_cutted'] = item.url[:50] + '...'
    context['categories'] = get_categories_list(item.categories)
    context['item_info'] = str(_('created:').capitalize()) + nice_date(item.created.date())

    store_params = get_store_params(request.user)

    params = 0
    if store_params.uc:
        params += 1
    if store_params.lc:
        params += 2
    if store_params.dg:
        params += 4
    if store_params.sp:
        params += 8
    if store_params.br:
        params += 16
    if store_params.mi:
        params += 32
    if store_params.ul:
        params += 64
    if store_params.ac:
        params += 128

    context['default_len'] = store_params.ln
    context['default_params'] = params

    return False


def item_delete(request, kind, art_id):
    if (kind == 'item'):
        data = get_object_or_404(Entry.objects.filter(user = request.user.id, id = art_id))
        data.delete()
        set_article_visible(request.user, app_name, False)


def get_store_params(user):
    if Params.objects.filter(user = user.id).exists():
        return Params.objects.filter(user = user.id).get()
    else:
        return Params.objects.create(user = user, ln = 30, uc = True, lc = True, dg = True, sp = True, br = True, mi = True, ul = True, ac = False)


def process_sort_commands(request):
    if ('sort_delete' in request.POST):
        set_sort_mode(request.user, app_name, '')
        return True
    if ('sort_title' in request.POST):
        set_sort_mode(request.user, app_name, 'title')
        return True
    if ('sort_user' in request.POST):
        set_sort_mode(request.user, app_name, 'username')
        return True
    if ('sort_url' in request.POST):
        set_sort_mode(request.user, app_name, 'url')
        return True
    if ('sort_created' in request.POST):
        set_sort_mode(request.user, app_name, 'created')
        return True
    if ('sort_direction' in request.POST):
        toggle_sort_dir(request.user, app_name)
        return True
    return False


#----------------------------------
# Parameters
#----------------------------------
def get_params(user):
    if (len(Params.objects.filter(user = user.id)) > 0):
        return Params.objects.filter(user = user.id)[0]
    else:
        return Params.objects.create(user = user)

#----------------------------------
def make_random_string(user):
    params = get_params(user)
    allowed_chars = ''
    
    if params.uc:
        allowed_chars = allowed_chars + 'ABCDEFGHJKLMNPQRSTUVWXYZ'
        if not params.ac:
            allowed_chars = allowed_chars + 'IO'
    
    if params.lc:
        allowed_chars = allowed_chars + 'abcdefghjkmnpqrstuvwxyz'
        if not params.ac:
            allowed_chars = allowed_chars + 'io'

    if params.dg:
        allowed_chars = allowed_chars + '23456789'
        if not params.ac:
            allowed_chars = allowed_chars + '10'

    if params.sp:
        allowed_chars = allowed_chars + '!@#$%^&*=+'

    if params.br:
        allowed_chars = allowed_chars + '()[]{}<>'
    
    if params.mi:
        allowed_chars = allowed_chars + '-'
    
    if params.ul:
        allowed_chars = allowed_chars + '_'

    if (allowed_chars == ''):
        allowed_chars = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789!@#$%^&*(-_=+)'

    return get_random_string(params.ln, allowed_chars)



