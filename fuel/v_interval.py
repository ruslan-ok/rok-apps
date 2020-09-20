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
from .models import app_name, Car, Fuel, Part, Repl, enrich_context
from .forms import PartForm


items_in_page = 10


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def interval_list(request):
    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('fuel:interval_list'))

    if not Car.objects.filter(user = request.user.id, active = True).exists():
        return HttpResponseRedirect(reverse('fuel:car_list'))

    car = Car.objects.filter(user = request.user.id, active = True).get()

    if (request.method == 'POST'):
        if ('item-add' in request.POST):
            item = Part.objects.create(car = car, name = request.POST['item_name_add'])
            return HttpResponseRedirect(reverse('fuel:interval_form', args = [item.id]))

    app_param, context = get_base_context_ext(request, app_name, 'interval', _('service intervals').capitalize() + ' [' + car.name + ']')
    template_file = 'fuel/interval_list.html'

    if app_param.article:
        redirect = False
        if (app_param.kind != 'interval'):
            set_article_visible(request.user, app_name, False)
            redirect = True
        elif Part.objects.filter(car = car.id, id = app_param.art_id).exists():
            redirect = item_article(request, context, car, app_param.art_id)
        else:
            set_article_visible(request.user, app_name, False)
            redirect = True
    
        if redirect:
            return HttpResponseRedirect(reverse('fuel:interval_list'))
        else:
            template_file = 'fuel/interval_form.html'

    query = None
    if request.method == 'GET':
        query = request.GET.get('q')
    data = filtered_sorted_list(car, query, app_param)
    items = []
    for d in data:
        items.append([d, get_item_info(d, app_param)])

    if request.method != 'GET':
        page_number = 1
    else:
        page_number = request.GET.get('page')
    paginator = Paginator(items, items_in_page)
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = page_obj
    context['search_info'] = get_search_info(query)
    context['cur_view'] = 'intervals'
    context = enrich_context(context, app_param, request.user.id)
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def interval_form(request, pk):
    set_article_kind(request.user, app_name, 'interval', pk)
    return HttpResponseRedirect(reverse('fuel:interval_list'))


#----------------------------------
def filtered_sorted_list(car, query, app_param):
    data = filtered_list(car, query)

    if not data:
        return data

    return sort_data(data, app_param.sort, app_param.reverse)

#----------------------------------
def filtered_list(car, query):
    data = Part.objects.filter(car = car.id)

    if not query:
        return data

    search_mode = get_search_mode(query)
    lookups = None
    if (search_mode == 0):
        return data
    elif (search_mode == 1):
        lookups = Q(name__icontains=query) | Q(comment__icontains=query)

    return data.filter(lookups).distinct()

#----------------------------------
def item_article(request, context, car, pk):
    item = get_object_or_404(Part.objects.filter(id = pk))
    form = None
    if (request.method == 'POST'):
        if ('article_delete' in request.POST):
            if item_delete(request, item):
                return True
        if ('item-save' in request.POST):
            form = PartForm(request.POST, instance = item)
            if form.is_valid():
                data = form.save(commit = False)
                data.car = car
                form.save()
                return True

    if not form:
        form = PartForm(instance = item)

    context['form'] = form
    context['item_id'] = item.id
    return False

#----------------------------------
def item_delete(request, item):
    if Repl.objects.filter(part = item.id).exists():
        return False

    item.delete()
    set_article_visible(request.user, app_name, False)
    return True

#----------------------------------
def get_item_info(item, app_param):
    ret = []
    
    if item.chg_km:
        ret.append({'text': _('km: ') + str(item.chg_km)})

    if item.chg_mo:
        if (len(ret) > 0):
            ret.append({'icon': 'separator'})
        ret.append({'text': _('months: ') + str(item.chg_mo)})

    rest, color = item.get_rest()
    if rest:
        #raise Exception(rest, color)
        if (len(ret) > 0):
            ret.append({'icon': 'separator'})
        ret.append({'text': rest, 'color': 'rest-color-' + color})
    
    if item.comment:
        if (len(ret) > 0):
            ret.append({'icon': 'separator'})
        ret.append({'icon': 'notes'})

    return ret


