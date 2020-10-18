from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q

from hier.utils import get_base_context_ext, process_common_commands, extract_get_params, sort_data
from hier.params import set_article_visible, set_article_kind, set_restriction, get_search_mode, get_search_info
from hier.models import get_app_params
from hier.aside import Fix
from .models import app_name, Car, set_active, Fuel, Part, Repl, consumption
from .forms import CarForm, FuelForm, PartForm, ReplForm

items_per_page = 10

#----------------------------------
def get_title(restriction, car):
    if (restriction == 'cars'):
        return _('cars').capitalize()
    if (restriction == 'fuel'):
        return _('fuelings').capitalize() + ' [' + car.name + ']'
    if (restriction == 'interval'):
        return _('service intervals').capitalize() + ' [' + car.name + ']'
    if (restriction == 'service'):
        return _('repair and service').capitalize() + ' [' + car.name + ']'
    return 'unknown restriction: ' + str(restriction)

#----------------------------------
def get_template_file(restriction):
    if (restriction == 'cars'):
        return 'fuel/car.html'
    if (restriction == 'fuel'):
        return 'fuel/fueling.html'
    if (restriction == 'interval'):
        return 'fuel/interval.html'
    if (restriction == 'service'):
        return 'fuel/service.html'
    return 'fuel/fuel.html'

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def main(request):
    app_param = get_app_params(request.user, app_name)
    if (app_param.restriction != 'cars') and (app_param.restriction != 'fuel') and (app_param.restriction != 'interval') and (app_param.restriction != 'service'):
        set_restriction(request.user, app_name, 'fuel')
        return HttpResponseRedirect(reverse('fuel:main') + extract_get_params(request))

    if not Car.objects.filter(user = request.user.id, active = True).exists():
        set_restriction(request.user, app_name, 'cars')
        return HttpResponseRedirect(reverse('fuel:main'))

    car = Car.objects.filter(user = request.user.id, active = True).get()

    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('fuel:main') + extract_get_params(request))

    form = None
    if (request.method == 'POST'):
        #raise Exception(request.POST)
        if ('item-add' in request.POST):
            if (app_param.restriction == 'cars'):
                item_id = add_car(request)
            if (app_param.restriction == 'fuel'):
                item_id = add_fuel(request, car)
            if (app_param.restriction == 'interval'):
                item_id = add_interval(request, car)
            if (app_param.restriction == 'service'):
                item_id = add_service(request, car)
            return HttpResponseRedirect(reverse('fuel:item_form', args = [item_id]))
        if ('item-in-list-select' in request.POST) and (app_param.restriction == 'cars'):
            pk = request.POST['item-in-list-select']
            if pk:
                set_active(request.user.id, pk)
                return HttpResponseRedirect(reverse('fuel:item_form', args = [pk]))

    app_param, context = get_base_context_ext(request, app_name, 'main', get_title(app_param.restriction, car))

    redirect = False

    if app_param.article:
        valid_article = False
        if (app_param.restriction == 'cars'):
            valid_article = Car.objects.filter(id = app_param.art_id, user = request.user.id).exists()
        if (app_param.restriction == 'fuel'):
            valid_article = Fuel.objects.filter(car = car.id, id = app_param.art_id).exists()
        if (app_param.restriction == 'interval'):
            valid_article = Part.objects.filter(car = car.id, id = app_param.art_id).exists()
        if (app_param.restriction == 'service'):
            valid_article = Repl.objects.filter(car = car.id, id = app_param.art_id).exists()
        if valid_article:
            if (app_param.restriction == 'cars'):
                item = get_object_or_404(Car.objects.filter(id = app_param.art_id, user = request.user.id))
                disable_delete = item.active or Fuel.objects.filter(car = item.id).exists() or Part.objects.filter(car = item.id).exists() or Repl.objects.filter(car = item.id).exists()
                redirect = edit_item(request, context, app_param.restriction, None, item, disable_delete)
            if (app_param.restriction == 'fuel'):
                item = get_object_or_404(Fuel.objects.filter(id = app_param.art_id))
                redirect = edit_item(request, context, app_param.restriction, car, item)
            if (app_param.restriction == 'interval'):
                item = get_object_or_404(Part.objects.filter(id = app_param.art_id))
                disable_delete = Repl.objects.filter(part = item.id).exists()
                redirect = edit_item(request, context, app_param.restriction, car, item, disable_delete)
            if (app_param.restriction == 'service'):
                item = get_object_or_404(Repl.objects.filter(id = app_param.art_id))
                redirect = edit_item(request, context, app_param.restriction, car, item)
        else:
            set_article_visible(request.user, app_name, False)
            redirect = True
    
    if redirect:
        return HttpResponseRedirect(reverse('fuel:main') + extract_get_params(request))

    fixes = []
    fixes.append(Fix('cars', _('cars').capitalize(), 'rok/icon/car.png', 'cars/', len(Car.objects.filter(user = request.user.id))))
    fixes.append(Fix('fuel', _('fuelings').capitalize(), 'rok/icon/gas.png', 'fuels/', len(Fuel.objects.filter(car = car))))
    fixes.append(Fix('interval', _('service intervals').capitalize(), 'todo/icon/remind-today.png', 'intervals/', len(Part.objects.filter(car = car))))
    fixes.append(Fix('service', _('repair and service').capitalize(), 'todo/icon/myday.png', 'services/', len(Repl.objects.filter(car = car))))
    context['fix_list'] = fixes
    context['without_lists'] = True
    context['hide_important'] = True
    if (app_param.restriction == 'cars'):
        context['add_item_placeholder'] = _('add car').capitalize()
    else:
        context['hide_selector'] = True
    if (app_param.restriction == 'fuel'):
        context['hide_add_item_input'] = True
    if (app_param.restriction == 'interval'):
        context['add_item_placeholder'] = _('add spare part').capitalize()
    if (app_param.restriction == 'service'):
        context['hide_add_item_input'] = True

    query = None
    if request.method == 'GET':
        query = request.GET.get('q')
    context['search_info'] = get_search_info(query)
    data = filtered_sorted_list(request.user, app_param.restriction, car, query)
    page_number = 1
    if (request.method == 'GET'):
        page_number = request.GET.get('page')
    paginator = Paginator(data, items_per_page)
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = paginator.get_page(page_number)

    template = loader.get_template(get_template_file(app_param.restriction))
    return HttpResponse(template.render(context, request))

def item_form(request, pk):
    set_article_kind(request.user, app_name, '', pk)
    return HttpResponseRedirect(reverse('fuel:main') + extract_get_params(request))

def go_cars(request):
    set_restriction(request.user, app_name, 'cars')
    return HttpResponseRedirect(reverse('fuel:main'))

def go_fuels(request):
    set_restriction(request.user, app_name, 'fuel')
    return HttpResponseRedirect(reverse('fuel:main'))

def go_intervals(request):
    set_restriction(request.user, app_name, 'interval')
    return HttpResponseRedirect(reverse('fuel:main'))

def go_services(request):
    set_restriction(request.user, app_name, 'service')
    return HttpResponseRedirect(reverse('fuel:main'))

#----------------------------------
def filtered_list(user, restriction, car, query = None):
    if (restriction == 'cars'):
        data = Car.objects.filter(user = user.id)
    elif (restriction == 'fuel'):
        data = Fuel.objects.filter(car = car.id)
    elif (restriction == 'interval'):
        data = Part.objects.filter(car = car.id)
    elif (restriction == 'service'):
        data = Repl.objects.filter(car = car.id)
    else:
        data = []

    if not query:
        return data

    search_mode = get_search_mode(query)
    lookups = None
    if (search_mode != 1):
        return data

    if (restriction == 'cars'):
        lookups = Q(name__icontains=query) | Q(plate__icontains=query)
    elif (restriction == 'fuel'):
        lookups = Q(comment__icontains=query)
    elif (restriction == 'interval'):
        lookups = Q(name__icontains=query) | Q(comment__icontains=query)
    elif (restriction == 'service'):
        lookups = Q(manuf__icontains=query) | Q(part_num__icontains=query) | Q(name__icontains=query) | Q(comment__icontains=query)
    else:
        return data

    return data.filter(lookups).distinct()

def filtered_sorted_list(user, restriction, car, query):
    data = filtered_list(user, restriction, car, query)

    if not data:
        return data

    if (restriction == 'cars'):
        return sort_data(data, 'name', False)

    if (restriction == 'fuel'):
        return data.order_by('-pub_date')
    
    if (restriction == 'interval'):
        return data.order_by('name')
    
    if (restriction == 'service'):
        return data.order_by('-dt_chg')
    
    return data

#----------------------------------
def add_car(request):
    item = Car.objects.create(user = request.user, name = request.POST['item_add-name'])
    return item.id

def add_fuel(request, car):
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

    item = Fuel.objects.create(car = car, pub_date = datetime.now(), odometr = new_odo, volume = new_vol, price = new_prc)
    return item.id

def add_interval(request, car):
    item = Part.objects.create(car = car, name = request.POST['item_add-name'])
    return item.id

def add_service(request, car):
    last = Fuel.objects.filter(car = car.id).order_by('-pub_date')[:1]
    new_odo = 0

    if (len(last) != 0):
        new_odo = last[0].odometr

    item = Repl.objects.create(car = car, dt_chg = datetime.now(), odometr = new_odo)
    return item.id

#----------------------------------
def edit_item(request, context, restriction, car, item, disable_delete = False):
    form = None
    if (request.method == 'POST'):
        if ('article_delete' in request.POST):
            delete_item(request, item, disable_delete)
            return True
        if ('item-save' in request.POST):
            if (restriction == 'cars'):
                form = CarForm(request.POST, instance = item)
            elif (restriction == 'fuel'):
                form = FuelForm(request.POST, instance = item)
            elif (restriction == 'interval'):
                form = PartForm(request.POST, instance = item)
            elif (restriction == 'service'):
                form = ReplForm(car, request.POST, instance = item)
            if form.is_valid():
                data = form.save(commit = False)
                if (restriction == 'cars'):
                    data.user = request.user
                else:
                    data.car = car
                form.save()
                return True

    if not form:
        if (restriction == 'cars'):
            form = CarForm(instance = item)
        elif (restriction == 'fuel'):
            form = FuelForm(instance = item)
        elif (restriction == 'interval'):
            form = PartForm(instance = item)
        elif (restriction == 'service'):
            form = ReplForm(car, instance = item)

    context['form'] = form
    context['ed_item'] = item
    return False

#----------------------------------
def delete_item(request, item, disable_delete = False):
    if disable_delete:
        return False
    item.delete()
    set_article_visible(request.user, app_name, False)
    return True






