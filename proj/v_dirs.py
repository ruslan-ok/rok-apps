from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.core.paginator import Paginator

from hier.utils import process_common_commands, get_base_context_ext, sort_data, extract_get_params
from hier.params import set_sort_mode, toggle_sort_dir, get_search_mode, get_search_info, set_article_kind, set_article_visible
from .models import app_name, Direct, set_active, Proj
from .forms import DirectForm

items_in_page = 10

SORT_MODE_DESCR = {
    '': '',
    'name': _('sort by name'),
    'created': _('sort by creation date'),
    'last_mod': _('sort by last modification date'),
}


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def dirs_list(request):
    if process_common_commands(request, app_name): # aside open/close, article open/close
        return HttpResponseRedirect(reverse('proj:dirs_list') + extract_get_params(request))

    if process_sort_commands(request):
        return HttpResponseRedirect(reverse('proj:dirs_list') + extract_get_params(request))

    if (request.method == 'POST'):
        #raise Exception(request.POST)
        if ('item-add' in request.POST):
            item = Direct.objects.create(user = request.user, name = request.POST['item_name_add'])
            return HttpResponseRedirect(reverse('proj:dirs_form', args = [item.id]))
        if ('item-active' in request.POST):
            pk = request.POST['item-active']
            if pk:
                set_active(request.user.id, pk)
                return HttpResponseRedirect(reverse('proj:dirs_form', args = [pk]))

    app_param, context = get_base_context_ext(request, app_name, 'dirs', _('projects').capitalize())

    direct = None
    if Direct.objects.filter(user = request.user.id, active = True).exists():
        direct = Direct.objects.filter(user = request.user.id, active = True).get()

    context['cur_view'] = 'dirs'
    context['dirs_qty'] = len(Direct.objects.filter(user = request.user.id))
    if direct:
        context['proj_qty'] = len(Proj.objects.filter(direct = direct))

    if app_param.sort:
        context['sort_mode'] = SORT_MODE_DESCR[app_param.sort].capitalize()
    context['sort_dir'] = not app_param.reverse

    template_file = 'proj/dirs_list.html'
    
    redirect = False
    if app_param.article:
        if (app_param.kind == 'dirs'):
            if not Direct.objects.filter(id = app_param.art_id, user = request.user.id).exists():
                set_article_visible(request.user, app_name, False)
                redirect = True
            else:
                redirect = item_details(request, context, app_param)
                if not redirect:
                    template_file = 'proj/dirs_form.html'

    if redirect:
        return HttpResponseRedirect(reverse('proj:dirs_list') + extract_get_params(request))

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
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))


#----------------------------------
def dirs_form(request, pk):
    set_article_kind(request.user, app_name, 'dirs', pk)
    return HttpResponseRedirect(reverse('proj:dirs_list') + extract_get_params(request))


#----------------------------------
def filtered_sorted_list(user, app_param, query):
    data = filtered_list(user, query)

    if not data:
        return data

    return sort_data(data, app_param.sort, app_param.reverse)

#----------------------------------
def filtered_list(user, query):
    data = Direct.objects.filter(user = user.id)

    if not query:
        return data

    search_mode = get_search_mode(query)
    lookups = None
    if (search_mode == 0):
        return data

    lookups = Q(name__icontains=query)
    return data.filter(lookups).distinct()

#----------------------------------
def process_sort_commands(request):
    if ('sort-delete' in request.POST):
        set_sort_mode(request.user, app_name, '')
        return True
    if ('sort-name' in request.POST):
        set_sort_mode(request.user, app_name, 'name')
        return True
    if ('sort-created' in request.POST):
        set_sort_mode(request.user, app_name, 'created')
        return True
    if ('sort-lmod' in request.POST):
        set_sort_mode(request.user, app_name, 'last_mod')
        return True
    if ('sort-direction' in request.POST):
        toggle_sort_dir(request.user, app_name)
        return True
    return False

#----------------------------------
def item_details(request, context, app_param):
    if not Direct.objects.filter(user = request.user.id, id = app_param.art_id).exists():
        set_article_visible(request.user, app_name, False)
        return True

    item = Direct.objects.filter(user = request.user.id, id = app_param.art_id).get()

    form = None

    if (request.method == 'POST'):
        #raise Exception(request.POST)
        if ('article_delete' in request.POST):
            if delete_item(request, app_param.art_id):
                return True
        if ('item-save' in request.POST):
            form = DirectForm(request.POST, instance = item)
            if form.is_valid():
                data = form.save(commit = False)
                data.user = request.user
                form.save()
                return True

    if not form:
        form = DirectForm(instance = item)

    context['form'] = form
    context['item_id'] = item.id
    return False


#----------------------------------
def delete_item(request, art_id):
    item = Direct.objects.filter(user = request.user.id, id = art_id).get()
    if Proj.objects.filter(direct = item.id).exists():
        return False
    item.delete()
    set_article_visible(request.user, app_name, False)
    return True
