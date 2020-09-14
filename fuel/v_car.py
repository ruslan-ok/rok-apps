from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q

from hier.utils import get_base_context_ext, process_common_commands, sort_data
from hier.params import set_article_visible, set_article_kind, get_search_mode, get_search_info
from .models import app_name, Car, set_active, Fuel, Part, Repl, enrich_context
from .forms import CarForm


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def car_list(request):
    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('fuel:car_list'))

    if (request.method == 'POST'):
        if ('item-add' in request.POST):
            item = Car.objects.create(user = request.user, name = request.POST['item_name_add'])
            return HttpResponseRedirect(reverse('fuel:car_form', args = [item.id]))
        if ('item-active' in request.POST):
            pk = request.POST['item-active']
            if pk:
                set_active(request.user.id, pk)
                return HttpResponseRedirect(reverse('fuel:car_form', args = [pk]))

    app_param, context = get_base_context_ext(request, app_name, 'car', _('cars'))
    template_file = 'fuel/car_list.html'

    if app_param.article:
        redirect = False
        if (app_param.kind != 'car'):
            set_article_visible(request.user, app_name, False)
            redirect = True
        elif Car.objects.filter(id = app_param.art_id, user = request.user.id).exists():
            redirect = item_article(request, context, app_param.art_id)
        else:
            set_article_visible(request.user, app_name, False)
            redirect = True
    
        if redirect:
            return HttpResponseRedirect(reverse('fuel:car_list'))
        else:
            template_file = 'fuel/car_form.html'

    query = None
    if request.method == 'GET':
        query = request.GET.get('q')
    data = filtered_sorted_list(request.user, app_param, query)
    if request.method != 'GET':
        page_number = 1
    else:
        page_number = request.GET.get('page')
    paginator = Paginator(data, 20)
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = page_obj
    context['search_info'] = get_search_info(query)
    context['cur_view'] = 'cars'
    context = enrich_context(context, app_param, request.user.id)
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def car_form(request, pk):
    set_article_kind(request.user, app_name, 'car', pk)
    return HttpResponseRedirect(reverse('fuel:car_list'))


#----------------------------------
def filtered_sorted_list(user, app_param, query):
    data = filtered_list(user, app_param.restriction, query, app_param.lst)

    if not data:
        return data

    return sort_data(data, app_param.sort, app_param.reverse)


#----------------------------------
def filtered_list(user, restriction, query = None, lst = None):
    data = Car.objects.filter(user = user.id)

    if not query:
        return data

    search_mode = get_search_mode(query)
    lookups = None
    if (search_mode == 0):
        return data
    elif (search_mode == 1):
        lookups = Q(name__icontains=query) | Q(plate__icontains=query)

    return data.filter(lookups).distinct()

#----------------------------------
def item_article(request, context, pk):
    item = get_object_or_404(Car.objects.filter(id = pk, user = request.user.id))
    form = None
    if (request.method == 'POST'):
        if ('article_delete' in request.POST):
            item_delete(request, item)
            return True
        if ('item-save' in request.POST):
            form = CarForm(request.POST, instance = item)
            if form.is_valid():
                data = form.save(commit = False)
                data.user = request.user
                form.save()
                return True

    if not form:
        form = CarForm(instance = item)

    context['form'] = form
    context['item_id'] = item.id
    context['item_active'] = item.active
    return False

#----------------------------------
def item_delete(request, item):
    if Fuel.objects.filter(car = item.id).exists() or Part.objects.filter(car = item.id).exists() or Repl.objects.filter(car = item.id).exists():
        return False

    item.delete()
    set_article_visible(request.user, app_name, False)
    return True

