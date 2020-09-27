from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.core.paginator import Paginator

from hier.utils import process_common_commands, get_base_context_ext, sort_data, extract_get_params
from hier.params import set_sort_mode, toggle_sort_dir, get_search_mode, get_search_info, set_article_kind, set_article_visible
from todo.utils import nice_date
from .models import app_name, Direct, Proj
from .forms import ProjForm

items_in_page = 10

SORT_MODE_DESCR = {
    '': '',
    'date': _('sort by date'),
    'kontr': _('sort by contractor'),
    'text': _('sort by description'),
    'created': _('sort by creation date'),
    'last_mod': _('sort by last modification date'),
}


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def proj_list(request):
    if not Direct.objects.filter(user = request.user.id, active = True).exists():
        return HttpResponseRedirect(reverse('proj:dirs_list'))

    direct = Direct.objects.filter(user = request.user.id, active = True).get()

    if process_common_commands(request, app_name): # aside open/close, article open/close
        return HttpResponseRedirect(reverse('proj:proj_list') + extract_get_params(request))

    if process_sort_commands(request):
        return HttpResponseRedirect(reverse('proj:proj_list') + extract_get_params(request))

    if (request.method == 'POST'):
        #raise Exception(request.POST)
        if ('item-add' in request.POST):
            item = item_add(request, direct)
            return HttpResponseRedirect(reverse('proj:proj_form', args = [item.id]))

    app_param, context = get_base_context_ext(request, app_name, 'proj', '{} [{}]'.format(_('expenses').capitalize(), direct.name))

    context['dirs_qty'] = len(Direct.objects.filter(user = request.user.id))
    context['proj_qty'] = len(Proj.objects.filter(direct = direct))

    if app_param.sort:
        context['sort_mode'] = SORT_MODE_DESCR[app_param.sort].capitalize()
    context['sort_dir'] = not app_param.reverse

    template_file = 'proj/proj_list.html'
    
    redirect = False
    if app_param.article:
        if (app_param.kind == 'proj'):
            if not Proj.objects.filter(id = app_param.art_id, direct = direct).exists():
                set_article_visible(request.user, app_name, False)
                redirect = True
            else:
                redirect = item_details(request, context, app_param, direct)
                if not redirect:
                    template_file = 'proj/proj_form.html'

    if redirect:
        return HttpResponseRedirect(reverse('proj:proj_list') + extract_get_params(request))

    query = None
    if request.method == 'GET':
        query = request.GET.get('q')
    data = filtered_sorted_list(direct, app_param, query)

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
def proj_form(request, pk):
    set_article_kind(request.user, app_name, 'proj', pk)
    return HttpResponseRedirect(reverse('proj:proj_list') + extract_get_params(request))


#----------------------------------
def item_add(request, direct):
    rate = get_rate_on_date(145, datetime.now())
    item = Proj.objects.create(direct = direct, course = rate)
    return item

#----------------------------------
def filtered_sorted_list(direct, app_param, query):
    data = filtered_list(direct, query)

    if not data:
        return data

    return sort_data(data, app_param.sort, app_param.reverse)

#----------------------------------
def filtered_list(direct, query):
    data = Proj.objects.filter(direct = direct)

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
    if ('sort-date' in request.POST):
        set_sort_mode(request.user, app_name, 'date')
        return True
    if ('sort-kontr' in request.POST):
        set_sort_mode(request.user, app_name, 'kontr')
        return True
    if ('sort-text' in request.POST):
        set_sort_mode(request.user, app_name, 'text')
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
def item_details(request, context, app_param, direct):
    if not Proj.objects.filter(id = app_param.art_id, direct = direct).exists():
        set_article_visible(request.user, app_name, False)
        return True

    item = Proj.objects.filter(id = app_param.art_id, direct = direct).get()

    form = None

    if (request.method == 'POST'):
        #raise Exception(request.POST)
        if ('article_delete' in request.POST):
            if delete_item(request, app_param.art_id):
                return True
        if ('item-save' in request.POST):
            form = ProjForm(request.POST, instance = item)
            if form.is_valid():
                data = form.save(commit = False)
                data.direct = direct
                form.save()
                return True

    if not form:
        form = ProjForm(instance = item)

    context['form'] = form
    context['item_id'] = item.id
    context['item_info'] = str(_('created:').capitalize()) + nice_date(item.created.date())

    return False



#----------------------------------
def delete_item(request, art_id):
    item = Proj.objects.filter(id = art_id).get()
    item.delete()
    set_article_visible(request.user, app_name, False)
    return True


