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
from .models import app_name, Car, Fuel, enrich_context, consumption
from .forms import FuelForm


items_in_page = 10


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def fueling_list(request):
    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('fuel:fueling_list'))

    if not Car.objects.filter(user = request.user.id, active = True).exists():
        return HttpResponseRedirect(reverse('fuel:car_list'))

    car = Car.objects.filter(user = request.user.id, active = True).get()

    if (request.method == 'POST'):
        if ('item-add' in request.POST):
            item = item_add(car)
            return HttpResponseRedirect(reverse('fuel:fueling_form', args = [item.id]))

    app_param, context = get_base_context_ext(request, app_name, 'fueling', _('fuelings'))
    template_file = 'fuel/fueling_list.html'

    if app_param.article:
        redirect = False
        if (app_param.kind != 'fueling'):
            set_article_visible(request.user, app_name, False)
            redirect = True
        elif Fuel.objects.filter(car = car.id, id = app_param.art_id).exists():
            redirect = item_article(request, context, car, app_param.art_id)
        else:
            set_article_visible(request.user, app_name, False)
            redirect = True
    
        if redirect:
            return HttpResponseRedirect(reverse('fuel:fueling_list'))
        else:
            template_file = 'fuel/fueling_form.html'

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
    context['cur_view'] = 'fuelings'
    context = enrich_context(context, app_param, request.user.id)
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def fueling_form(request, pk):
    set_article_kind(request.user, app_name, 'fueling', pk)
    return HttpResponseRedirect(reverse('fuel:fueling_list'))


#----------------------------------
def filtered_sorted_list(car, query, app_param):
    data = filtered_list(car, query)

    if not data:
        return data

    #return sort_data(data, app_param.sort, app_param.reverse)
    return data.order_by('-pub_date')

#----------------------------------
def filtered_list(car, query):
    data = Fuel.objects.filter(car = car.id)

    if not query:
        return data

    search_mode = get_search_mode(query)
    lookups = None
    if (search_mode == 0):
        return data
    elif (search_mode == 1):
        lookups = Q(odometr__icontains=query) | Q(comment__icontains=query) | Q(pub_date__icontains=query)

    return data.filter(lookups).distinct()

#----------------------------------
def item_article(request, context, car, pk):
    item = get_object_or_404(Fuel.objects.filter(id = pk))
    form = None
    if (request.method == 'POST'):
        if ('article_delete' in request.POST):
            if item_delete(request, item):
                return True
        if ('item-save' in request.POST):
            form = FuelForm(request.POST, instance = item)
            if form.is_valid():
                data = form.save(commit = False)
                data.car = car
                form.save()
                return True

    if not form:
        form = FuelForm(instance = item)

    context['form'] = form
    context['item_id'] = item.id
    return False

#----------------------------------
def item_add(car):
    last = Fuel.objects.filter(car = car.id).order_by('-pub_date')[:3]
    new_odo = 0
    new_prc = 0

    if (len(last) == 0):
        new_vol = 25
    else:
        new_vol = last[0].volume
        new_prc = last[0].price
        if (len(last) > 2):
            if (last[0].volume != last[1].volume) and (last[1].volume == last[2].volume):
                new_vol = last[1].volume
                new_prc = last[1].price

        cons = consumption(None, car)
        if (cons != 0):
            new_odo = last[0].odometr + int(last[0].volume / cons * 100)

    return Fuel.objects.create(car = car, pub_date = datetime.now(), odometr = new_odo, volume = new_vol, price = new_prc)

#----------------------------------
def item_delete(request, item):
    item.delete()
    set_article_visible(request.user, app_name, False)
    return True

#----------------------------------
def get_item_info(item, app_param):
    ret = []
    ret.append({'text': _('odometr: ') + str(item.odometr)})
    ret.append({'icon': 'separator'})
    ret.append({'text': _('volume: ') + '{:.0f}'.format(item.volume)})
    ret.append({'icon': 'separator'})
    ret.append({'text': _('price: ') + '{:.2f}'.format(item.price)})
    ret.append({'icon': 'separator'})
    ret.append({'text': _('summa: ') + '{:.2f}'.format(item.summa())})
    if item.comment:
        ret.append({'icon': 'separator'})
        ret.append({'icon': 'notes'})
        ret.append({'text': item.comment})
    return ret

