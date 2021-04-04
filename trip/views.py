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
from .models import app_name, Trip, Saldo, Person, trip_summary, set_active, PERS, TRIP
from .forms import PersonForm, TripForm

items_per_page = 10

#----------------------------------
def get_template_file(restriction):
    if (restriction == PERS):
        return 'trip/person.html'
    return 'trip/trip.html'

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def main(request):
    app_param = get_app_params(request.user, app_name)
    if (app_param.restriction != PERS) and (app_param.restriction != TRIP):
        set_restriction(request.user, app_name, TRIP)
        return HttpResponseRedirect(reverse('trip:main') + extract_get_params(request))

    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('trip:main') + extract_get_params(request))

    form = None
    if (request.method == 'POST'):
        if ('item-add' in request.POST):
            if (app_param.restriction == TRIP):
                item_id = trip_add(request)
            if (app_param.restriction == PERS):
                item_id = pers_add(request)
            return HttpResponseRedirect(reverse('trip:item_form', args = [item_id]))
        if ('trip-count' in request.POST):
            do_count(request)
            return HttpResponseRedirect(reverse('trip:main'))
        if ('item-in-list-select' in request.POST) and (app_param.restriction == PERS):
            pk = request.POST['item-in-list-select']
            if pk:
                set_active(request.user.id, pk)
                return HttpResponseRedirect(reverse('trip:item_form', args = [pk]))

    app_param, context = get_base_context_ext(request, app_name, 'main', (app_param.restriction,))

    redirect = False

    if app_param.article:
        valid_article = False
        if (app_param.restriction == TRIP):
            valid_article = Trip.objects.filter(id = app_param.art_id, user = request.user.id).exists()
        if (app_param.restriction == PERS):
            valid_article = Person.objects.filter(id = app_param.art_id, user = request.user.id).exists()
        if valid_article:
            if (app_param.restriction == TRIP):
                redirect = get_trip_article(request, context, app_param.art_id)
            if (app_param.restriction == PERS):
                redirect = get_pers_article(request, context, app_param.art_id)
        else:
            set_article_visible(request.user, app_name, False)
            redirect = True
    
    if redirect:
        return HttpResponseRedirect(reverse('trip:main') + extract_get_params(request))

    fixes = []
    fixes.append(Fix(PERS, _('persons').capitalize(), 'rok/icon/user.png', 'persons/', len(Person.objects.filter(user = request.user.id))))
    fixes.append(Fix(TRIP, _('trips').capitalize(), 'rok/icon/car.png', 'trips/', len(Trip.objects.filter(user = request.user.id))))
    context['fix_list'] = fixes
    context['without_lists'] = True
    context['hide_important'] = True
    context['title_info'] = trip_summary(request.user.id, False)
    if (app_param.restriction == PERS):
        context['add_item_placeholder'] = _('add person').capitalize()
    if (app_param.restriction == TRIP):
        context['hide_add_item_input'] = True
        context['complete_icon']   = 'rok/icon/car.png'
        context['uncomplete_icon'] = 'rok/icon/cost.png'
        context['today'] = int(datetime.today().strftime('%w'))

    query = None
    if request.method == 'GET':
        query = request.GET.get('q')
    context['search_info'] = get_search_info(query)
    data = filtered_sorted_list(request.user, app_param.restriction, query)
    context['search_qty'] = len(data)
    context['search_data'] = query and (len(data) > 0)
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
    return HttpResponseRedirect(reverse('trip:main') + extract_get_params(request))

def go_persons(request):
    set_restriction(request.user, app_name, PERS)
    return HttpResponseRedirect(reverse('trip:main'))

def go_trips(request):
    set_restriction(request.user, app_name, TRIP)
    return HttpResponseRedirect(reverse('trip:main'))

def trip_entity(request, name, pk):
    set_restriction(request.user, app_name, name)
    set_article_kind(request.user, app_name, '', pk)
    return HttpResponseRedirect(reverse('trip:main'))

#----------------------------------
def filtered_list(user, restriction, query = None):
    if (restriction == PERS):
        data = Person.objects.filter(user = user.id)
    elif (restriction == TRIP):
        data = Trip.objects.filter(user = user.id)
    else:
        data = []

    if not query:
        return data

    search_mode = get_search_mode(query)
    lookups = None
    if (search_mode != 1):
        return data

    if (restriction == PERS):
        lookups = Q(name__icontains=query) | Q(dative__icontains=query)
    elif (restriction == TRIP):
        lookups = Q(text__icontains=query)
    else:
        return data

    return data.filter(lookups).distinct()

def filtered_sorted_list(user, restriction, query):
    data = filtered_list(user, restriction, query)

    if not data:
        return data

    if (restriction == PERS):
        return sort_data(data, '-me name', False)
    
    return sort_data(data, 'year week modif', True)

#----------------------------------
def get_trip_article(request, context, pk):
    ed_trip = get_object_or_404(Trip, id = pk)
    form = None
    if (request.method == 'POST'):
        if ('item_delete' in request.POST):
            trip_delete(request, ed_trip)
            return True
        if ('item_save' in request.POST):
            old_drvr = ed_trip.driver
            old_psgr = ed_trip.passenger
            old_oper = ed_trip.oper
            old_summa = ed_trip.summa()
            form = TripForm(request.user, request.POST, instance = ed_trip)
            if form.is_valid():
                trip = form.save(commit = False)
                trip.user = request.user
                trip.modif = datetime.now()
                if (trip.oper == 1):
                    trip.price = request.POST['summa']
                trip.save()
                saldo_update(request.user, old_drvr, old_psgr, old_oper, -1*old_summa)
                saldo_update(request.user, trip.driver, trip.passenger, trip.oper, trip.summa())
                return True
    else:
        ed_trip = get_object_or_404(Trip, id = pk)
        form = TripForm(request.user,
                        instance = ed_trip,
                        initial = { 'summa': ed_trip.summa(),
                                    'day_11': get_day(ed_trip.days, 1, 1),
                                    'day_12': get_day(ed_trip.days, 1, 2),
                                    'day_13': get_day(ed_trip.days, 1, 3),
                                    'day_14': get_day(ed_trip.days, 1, 4),
                                    'day_15': get_day(ed_trip.days, 1, 5),
                                    'day_16': get_day(ed_trip.days, 1, 6),
                                    'day_17': get_day(ed_trip.days, 1, 7),
                                    'day_21': get_day(ed_trip.days, 2, 1),
                                    'day_22': get_day(ed_trip.days, 2, 2),
                                    'day_23': get_day(ed_trip.days, 2, 3),
                                    'day_24': get_day(ed_trip.days, 2, 4),
                                    'day_25': get_day(ed_trip.days, 2, 5),
                                    'day_26': get_day(ed_trip.days, 2, 6),
                                    'day_27': get_day(ed_trip.days, 2, 7),
                                    })

    if not form:
        form = TripForm(instance = ed_trip)

    context['form'] = form
    context['ed_item'] = ed_trip
    return False


#----------------------------------
def trip_add(request):
    # Initializing the fields of a new record
    last_trip = Trip.objects.filter(user = request.user.id, oper = 0).order_by('-year', '-week', '-days')[:1]
    price_new  = 0
    drvr_new = None
    pass_new = None
    debt_sum = 0
    week_new = int(datetime.now().strftime("%W")) + 1
    
    if (len(last_trip) > 0): # last trip
        price_new = last_trip[0].price
        drvr_new  = last_trip[0].driver
        pass_new  = last_trip[0].passenger
    
    saldos = Saldo.objects.filter(user = request.user.id)
    for s in saldos:
        if (s.summ < 0):
            tmp = -1*s.summ
            if (debt_sum < tmp):
                debt_sum = tmp
                drvr_new = s.p2
                pass_new = s.p1
        else:
            if (debt_sum < s.summ):
                debt_sum = s.summ
                drvr_new = s.p1
                pass_new = s.p2

            form = TripForm(request.user,
                            initial = {'year':      datetime.now().year,
                                       'week':      week_new,
                                       'days':      0,
                                       'oper':      0,
                                       'price':     price_new,
                                       'driver':    drvr_new.id,
                                       'passenger': pass_new.id,
                                       'summa':     0, 
                                       'day_11': get_day(0, 1, 1),
                                       'day_12': get_day(0, 1, 2),
                                       'day_13': get_day(0, 1, 3),
                                       'day_14': get_day(0, 1, 4),
                                       'day_15': get_day(0, 1, 5),
                                       'day_16': get_day(0, 1, 6),
                                       'day_17': get_day(0, 1, 7),
                                       'day_21': get_day(0, 2, 1),
                                       'day_22': get_day(0, 2, 2),
                                       'day_23': get_day(0, 2, 3),
                                       'day_24': get_day(0, 2, 4),
                                       'day_25': get_day(0, 2, 5),
                                       'day_26': get_day(0, 2, 6),
                                       'day_27': get_day(0, 2, 7),
                                       'text':      '' })

    new_trip = Trip.objects.create(user = request.user, year = datetime.now().year, week = week_new, price = price_new, driver = drvr_new, passenger = pass_new)
    return new_trip.id

#----------------------------------
def trip_delete(request, trip):
    saldo_update(request.user, trip.driver, trip.passenger, trip.oper, -1*trip.summa())
    trip.delete()
    set_article_visible(request.user, app_name, False)
    return True

#----------------------------------
def get_me_code(_user):
    try:
        me = Person.objects.get(user = _user, me = True)
        return me.id
    except Person.DoesNotExist:
        return 0

#----------------------------------
def saldo_update(_user, _p1, _p2, _oper, _sum, debug = False):
    a1 = _p1
    a2 = _p2
    sm = _sum
    if (_p1.id > _p2.id):
        a1 = _p2
        a2 = _p1
        sm = -1*_sum
  
    if (_oper == 1):
        sm *= -1
  
    try:
        s = Saldo.objects.get(user = _user.id, p1 = a1.id, p2 = a2.id)
        if debug:
            raise Exception(s.summ, sm)
        if ((s.summ + sm) == 0):
            s.delete()
        else:
            s.summ += sm
            s.save()
    except Saldo.DoesNotExist:
        me_code = get_me_code(_user)
        is_me = 0
        if (a1.id == me_code) or (a2.id == me_code):
            is_me = 1
        s = Saldo(user = _user, p1 = a1, p2 = a2, me = is_me, summ = sm)
        s.save()

#----------------------------------
def do_count(request):
    Saldo.objects.filter(user = request.user.id).delete()
    trips = Trip.objects.filter(user = request.user.id)
    for t in trips:
        saldo_update(request.user, t.driver, t.passenger, t.oper, t.summa())

#----------------------------------
def get_day(days, row, col):
    return ((days & (1 << (row-1) + (col-1)*2)) != 0)


#----------------------------------
#----------------------------------
def pers_add(request):
    person = Person.objects.create(user = request.user, name = request.POST['item_add-name'])
    return person.id

#----------------------------------
def get_pers_article(request, context, pk):
    ed_person = get_object_or_404(Person.objects.filter(id = pk, user = request.user.id))
    form = None
    if (request.method == 'POST'):
        if ('item_delete' in request.POST):
            pers_delete(request, ed_person)
            return True
        if ('item_save' in request.POST):
            form = PersonForm(request.POST, instance = ed_person)
            if form.is_valid():
                data = form.save(commit = False)
                data.user = request.user
                form.save()
                return True

    if not form:
        form = PersonForm(instance = ed_person)

    context['form'] = form
    context['ed_item'] = ed_person
    return False

#----------------------------------
def pers_delete(request, person):
    if Trip.objects.filter(driver = person.id).exists() or Trip.objects.filter(passenger = person.id).exists():
        return False

    person.delete()
    set_article_visible(request.user, app_name, False)
    return True



