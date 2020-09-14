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

from hier.utils import get_base_context_ext, process_common_commands, sort_data
from hier.params import set_article_visible, set_restriction, set_aside_visible
from hier.categories import get_categories_list
from hier.grp_lst import group_add, group_details, group_toggle, list_add, list_details
from .models import Entry, Params
from .forms import EntryForm, ParamsForm
from hier.models import Folder
from hier.params import get_app_params, set_sort_mode, toggle_sort_dir, set_article_kind
from todo.models import Grp, Lst
from todo.utils import nice_date
from todo.tree import build_tree

app_name = 'store'
url_list = 'store:entry_list'
url_form = 'store:entry_form'
url_param = 'store:param_list'
template_form = 'store/entry_form.html'
template_list = 'store/entry_list.html'
template_list_details = 'store/list_form.html'
template_group_details = 'store/group_form.html'
template_param = 'store/param_list.html'
items_in_page = 10

SORT_MODE_DESCR = {
    '': '',
    'title': _('sort by title'),
    'username': _('sort by username'),
    'url': _('sort by URL'),
    'created': _('sort by create date')
}


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def entry_list(request):
    locale.setlocale(locale.LC_CTYPE, request.LANGUAGE_CODE)
    locale.setlocale(locale.LC_TIME, request.LANGUAGE_CODE)

    if process_common_commands(request, app_name): # aside open/close, article open/close
        return HttpResponseRedirect(reverse(url_list))

    if process_sort_commands(request):
        return HttpResponseRedirect(reverse(url_list))

    app_param = get_app_params(request.user, app_name)

    if (request.method == 'POST'):
        #raise Exception(request.POST)
        if ('item-add' in request.POST):
            item = Entry.objects.create(user = request.user, title = request.POST['item_add-name'], value = make_random_string(request.user), lst = app_param.lst)
            return HttpResponseRedirect(reverse(url_form, args = [item.id]))
        if ('list-add' in request.POST):
            lst_id = list_add(request.user, app_name, request.POST['name'])
            return HttpResponseRedirect(reverse('store:list_form', args = [lst_id]))
        if ('group-add' in request.POST):
            grp_id = group_add(request.user, app_name, request.POST['name'])
            return HttpResponseRedirect(reverse('store:group_form', args = [grp_id]))

    if (app_param.restriction == 'all'):
        title = _('all entries').capitalize()
    elif (app_param.restriction == 'actual'):
        title = _('actual entries').capitalize()
    elif (app_param.restriction == 'waste'):
        title = _('waste entries').capitalize()
    elif (app_param.restriction == 'list') and app_param.lst:
        lst = Lst.objects.filter(user = request.user.id, id = app_param.lst.id).get()
        title = lst.name
    else:
        title = _('entries with unknown restriction').capitalize()

    app_param, context = get_base_context_ext(request, app_name, 'entry', title)

    context['title'] = title + ' - ' + _('entries').capitalize()
    context['list_title'] = title
    if app_param.lst:
        context['list_id'] = app_param.lst.id
    context['restriction'] = app_param.restriction
    context['actual_qty'] = len(filtered_list(request.user, 'actual'))
    context['waste_qty'] = len(filtered_list(request.user, 'waste'))
    context['all_qty'] = len(filtered_list(request.user, 'all'))

    if app_param.sort:
        context['sort_mode'] = SORT_MODE_DESCR[app_param.sort].capitalize()
    context['sort_dir'] = not app_param.reverse

    tree = build_tree(request.user.id, 'store')
    for t in tree:
        if t.is_list:
            t.qty = len(Entry.objects.filter(user = request.user.id, lst = t.id))
    context['groups'] = tree

    template_file = template_list
    
    redirect = False
    if app_param.article:
        if (app_param.kind == 'item'):
            if not Entry.objects.filter(id = app_param.art_id, user = request.user.id).exists():
                set_article_visible(request.user, app_name, False)
                redirect = True
            else:
                template_file = template_form
                redirect = get_article_item(request, context, app_param)
        elif (app_param.kind == 'list'):
            can_delete = not Entry.objects.filter(lst = app_param.art_id).exists()
            redirect = list_details(request, context, app_param.art_id, app_name, can_delete)
            if not redirect:
                template_file = template_list_details
        elif (app_param.kind == 'group'):
            redirect = group_details(request, context, app_param.art_id, app_name)
            if not redirect:
                template_file = template_group_details

    if redirect:
        return HttpResponseRedirect(reverse(url_list))

    query = None
    if request.method == 'GET':
        query = request.GET.get('q')
    data = filtered_sorted_list(request.user, app_param, query)
    items = []
    for d in data:
        items.append([d, get_item_info(d, app_param)])

    page_number = 1
    if (request.method == 'GET'):
        page_number = request.GET.get('page')
    paginator = Paginator(items, items_in_page)
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = paginator.get_page(page_number)

    search_mode = get_search_mode(query)
    if (search_mode == 1):
        context['search_info'] = _('contained').capitalize() + ' "' + query + '"'
    elif (search_mode == 2):
        context['search_info'] = _('contained category').capitalize() + ' "' + query[1:] + '"'

    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def entry_form(request, pk):
    set_article_kind(request.user, app_name, 'item', pk)
    return HttpResponseRedirect(reverse(url_list))


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
        if ('article_delete' in request.POST):
            article_delete(request, app_param.kind, app_param.art_id)
            return True
        if ('item-save' in request.POST):
            form = EntryForm(request.POST, instance = item)
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
        if ('url-delete' in request.POST):
            item.url = ''
            item.save()
            return True
        if ('category-delete' in request.POST):
            category = request.POST['category-delete']
            item.categories = item.categories.replace(category, '')
            item.save()
            return True

    if not form:
        form = EntryForm(instance = item)

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


def article_delete(request, kind, art_id):
    if (kind == 'item'):
        data = get_object_or_404(Entry.objects.filter(user = request.user.id, id = art_id))
        data.delete()
        set_article_visible(request.user, app_name, False)


def actual(request):
    set_restriction(request.user, app_name, 'actual')
    return HttpResponseRedirect(reverse(url_list))


def waste(request):
    set_restriction(request.user, app_name, 'waste')
    return HttpResponseRedirect(reverse(url_list))


def all(request):
    set_restriction(request.user, app_name, 'all')
    return HttpResponseRedirect(reverse(url_list))


def param_list(request):
    locale.setlocale(locale.LC_CTYPE, request.LANGUAGE_CODE)
    locale.setlocale(locale.LC_TIME, request.LANGUAGE_CODE)

    if process_common_commands(request, app_name): # aside open/close
        return HttpResponseRedirect(reverse(url_param))

    store_params = get_store_params(request.user)

    form = None
    if (request.method == 'POST'):
        if ('param-save' in request.POST):
            form = ParamsForm(request.POST, instance = store_params)
            if form.is_valid():
                data = form.save(commit = False)
                data.user = request.user
                form.save()
                return HttpResponseRedirect(reverse(url_param))
        if ('list-add' in request.POST):
            lst_id = list_add(request.user, app_name, request.POST['name'])
            return HttpResponseRedirect(reverse('store:list_form', args = [lst_id]))
        if ('group-add' in request.POST):
            grp_id = group_add(request.user, app_name, request.POST['name'])
            return HttpResponseRedirect(reverse('store:group_form', args = [grp_id]))

    if not form:
        form = ParamsForm(instance = store_params)

    title = _('default parameters').capitalize()
    app_param, context = get_base_context_ext(request, app_name, 'param', title, article_enabled = False)
    context['form_title'] = title
    context['form'] = form
    context['restriction'] = 'default'
    context['actual_qty'] = len(filtered_list(request.user, 'actual'))
    context['waste_qty'] = len(filtered_list(request.user, 'waste'))
    context['all_qty'] = len(filtered_list(request.user, 'all'))
    
    template = loader.get_template(template_param)
    return HttpResponse(template.render(context, request))


def get_store_params(user):
    if Params.objects.filter(user = user.id).exists():
        return Params.objects.filter(user = user.id).get()
    else:
        return Params.objects.create(user = user, ln = 30, uc = True, lc = True, dg = True, sp = True, br = True, mi = True, ul = True, ac = False)


def get_search_mode(query):
    if not query:
        return 0
    if (len(query) > 1) and (query[0] == '#') and (query.find(' ') == -1):
        return 2
    else:
        return 1


def get_item_info(item, app_param):
    ret = []
    
    if item.lst and (app_param.restriction != 'list'):
        ret.append({'text': item.lst.name})

    if item.username:
        if (len(ret) > 0):
            ret.append({'icon': 'separator'})
        ret.append({'text': item.username})

    if item.notes:
        if (len(ret) > 0):
            ret.append({'icon': 'separator'})
        ret.append({'icon': 'notes'})

    if item.categories:
        if (len(ret) > 0):
            ret.append({'icon': 'separator'})
        categs = get_categories_list(item.categories)
        for categ in categs:
            ret.append({'icon': 'category', 'text': categ.name, 'color': 'category-design-' + categ.design})

    return ret


def process_sort_commands(request):
    if ('sort-delete' in request.POST):
        set_sort_mode(request.user, app_name, '')
        return True
    if ('sort-title' in request.POST):
        set_sort_mode(request.user, app_name, 'title')
        return True
    if ('sort-user' in request.POST):
        set_sort_mode(request.user, app_name, 'username')
        return True
    if ('sort-url' in request.POST):
        set_sort_mode(request.user, app_name, 'url')
        return True
    if ('sort-created' in request.POST):
        set_sort_mode(request.user, app_name, 'created')
        return True
    if ('sort-direction' in request.POST):
        toggle_sort_dir(request.user, app_name)
        return True
    return False



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
    return HttpResponseRedirect(reverse(url_list))

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



#======================================================================================================
def get_lst(user, folder_id):
    path = []
    ok = True
    lst_folder = None
    while folder_id:
        if not Folder.objects.filter(id = folder_id).exists():
            ok = False
            break
        f = Folder.objects.filter(id = folder_id).get()
        if not lst_folder:
            lst_folder = f
        else:
            if (f.model_name == 'store:entry_list'):
                if (f.name == 'Пароли'):
                    break
                path.append(f)
        folder_id = f.node
        
    if (not ok) or (not lst_folder):
        return ok, None
        
    grp = None
    for f in reversed(path):
        if Grp.objects.filter(user = user.id, app = 'store', node = grp, name = f.name).exists():
            grp = Grp.objects.filter(user = user.id, app = 'store', node = grp, name = f.name).get()
        else:
            grp = Grp.objects.create(user = user, app = 'store', node = grp, sort = f.code, is_open = f.is_open, name = f.name)

    if Lst.objects.filter(user = user.id, app = 'store', grp = grp, name = lst_folder.name).exists():
        return ok, Lst.objects.filter(user = user.id, app = 'store', grp = grp, name = lst_folder.name).get()

    return ok, Lst.objects.create(user = user, app = 'store', grp = grp, name = lst_folder.name, sort = lst_folder.code)


def convert(request):
    for e in Entry.objects.all():
        e.lst = None
        e.save()
    Lst.objects.filter(app = 'store').delete()
    Grp.objects.filter(app = 'store').delete()
    for e in Entry.objects.all():
        ok = False
        lst = None
        for f in Folder.objects.filter(user = e.user.id, content_id = e.id):
            if (f.model_name[:6] == 'store:'):
                ok, lst = get_lst(e.user, f.node)
                if ok:
                    break
        if ok:
            e.lst = lst
            e.save()
    return HttpResponseRedirect(reverse(url_list))






