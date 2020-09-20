from datetime import datetime

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
from .models import app_name, Car, Fuel, Repl, enrich_context, consumption
from .forms import ReplForm


items_in_page = 10


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def service_list(request):
    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('fuel:service_list'))

    if not Car.objects.filter(user = request.user.id, active = True).exists():
        return HttpResponseRedirect(reverse('fuel:car_list'))

    car = Car.objects.filter(user = request.user.id, active = True).get()

    if (request.method == 'POST'):
        if ('item-add' in request.POST):
            item = item_add(car)
            return HttpResponseRedirect(reverse('fuel:service_form', args = [item.id]))

    app_param, context = get_base_context_ext(request, app_name, 'service', _('repair and service').capitalize() + ' [' + car.name + ']')
    template_file = 'fuel/service_list.html'

    if app_param.article:
        redirect = False
        if (app_param.kind != 'service'):
            set_article_visible(request.user, app_name, False)
            redirect = True
        elif Repl.objects.filter(car = car.id, id = app_param.art_id).exists():
            redirect = item_article(request, context, car, app_param.art_id)
        else:
            set_article_visible(request.user, app_name, False)
            redirect = True
    
        if redirect:
            return HttpResponseRedirect(reverse('fuel:service_list'))
        else:
            template_file = 'fuel/service_form.html'

    query = None
    if request.method == 'GET':
        query = request.GET.get('q')
    data = filtered_sorted_list(car, query, app_param)
    items = []
    for d in data:
        items.append([d, get_item_info(d, app_param)])

    if (request.method != 'GET'):
        page_number = 1
    else:
        page_number = request.GET.get('page')
    paginator = Paginator(items, items_in_page)
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = page_obj
    context['search_info'] = get_search_info(query)
    context['cur_view'] = 'services'
    context = enrich_context(context, app_param, request.user.id)
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def service_form(request, pk):
    set_article_kind(request.user, app_name, 'service', pk)
    return HttpResponseRedirect(reverse('fuel:service_list'))


#----------------------------------
def filtered_sorted_list(car, query, app_param):
    data = filtered_list(car, query)

    if not data:
        return data

    #return sort_data(data, app_param.sort, app_param.reverse)
    return data.order_by('-dt_chg')

#----------------------------------
def filtered_list(car, query):
    data = Repl.objects.filter(car = car.id)

    if not query:
        return data

    search_mode = get_search_mode(query)
    lookups = None
    if (search_mode == 0):
        return data
    elif (search_mode == 1):
        lookups = Q(odometr__icontains=query) | Q(comment__icontains=query) | Q(manuf__icontains=query) | Q(part_num__icontains=query) | Q(name__icontains=query)

    return data.filter(lookups).distinct()

#----------------------------------
def item_article(request, context, car, pk):
    item = get_object_or_404(Repl.objects.filter(id = pk))
    form = None
    if (request.method == 'POST'):
        if ('article_delete' in request.POST):
            if item_delete(request, item):
                return True
        if ('item-save' in request.POST):
            form = ReplForm(car, request.POST, instance = item)
            if form.is_valid():
                data = form.save(commit = False)
                data.car = car
                form.save()
                return True

    if not form:
        form = ReplForm(car, instance = item)

    context['form'] = form
    context['item_id'] = item.id
    return False

#----------------------------------
def item_add(car):
    last = Fuel.objects.filter(car = car.id).order_by('-pub_date')[:1]
    new_odo = 0

    if (len(last) != 0):
        new_odo = last[0].odometr

    return Repl.objects.create(car = car, dt_chg = datetime.now(), odometr = new_odo)

#----------------------------------
def item_delete(request, item):
    item.delete()
    set_article_visible(request.user, app_name, False)
    return True

#----------------------------------
def get_item_info(item, app_param):
    ret = []
    ret.append({'text': _('odometr: ') + str(item.odometr)})
    if item.manuf:
        ret.append({'icon': 'separator'})
        ret.append({'text': item.manuf})
    if item.part_num:
        ret.append({'icon': 'separator'})
        ret.append({'text': item.part_num})
    if item.name:
        ret.append({'icon': 'separator'})
        ret.append({'text': item.name})
    if item.comment:
        ret.append({'icon': 'separator'})
        ret.append({'icon': 'notes'})
        ret.append({'text': item.comment})
    return ret

