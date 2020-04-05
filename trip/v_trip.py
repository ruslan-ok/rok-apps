from datetime import datetime
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Person, Saldo, Trip
from .forms import TripForm

def do_trip(request, pk):
    t = None
    if (request.method == 'GET'):
        if (pk != 0):
            t = get_object_or_404(Trip, pk = pk)
            form = TripForm(request.user,
                            instance = t,
                            initial = { 'summa': t.summa(),
                                        'day_11': get_day(t.days, 1, 1),
                                        'day_12': get_day(t.days, 1, 2),
                                        'day_13': get_day(t.days, 1, 3),
                                        'day_14': get_day(t.days, 1, 4),
                                        'day_15': get_day(t.days, 1, 5),
                                        'day_16': get_day(t.days, 1, 6),
                                        'day_17': get_day(t.days, 1, 7),
                                        'day_21': get_day(t.days, 2, 1),
                                        'day_22': get_day(t.days, 2, 2),
                                        'day_23': get_day(t.days, 2, 3),
                                        'day_24': get_day(t.days, 2, 4),
                                        'day_25': get_day(t.days, 2, 5),
                                        'day_26': get_day(t.days, 2, 6),
                                        'day_27': get_day(t.days, 2, 7),
                                        })
        else:
            # Инициализация полей новой записи
            last_trip = Trip.objects.filter(user = request.user.id, oper = 0).order_by('-year', '-week', '-days')[:1]
            price_new  = 0
            drvr_new = 2
            pass_new = 1
            debt_sum = 0
            week_new = int(datetime.now().strftime("%W")) + 1
        
            if (len(last_trip) > 0): # последняя поездка
                price_new = last_trip[0].price
                drvr_new  = last_trip[0].driver.id
                pass_new  = last_trip[0].passenger.id
        
            saldos = Saldo.objects.filter(user = request.user.id)
            for s in saldos:
                if (s.summ < 0):
                    tmp = -1*s.summ
                    if (debt_sum < tmp):
                        debt_sum = tmp
                        drvr_new = s.p2.id
                        pass_new = s.p1.id
                else:
                    if (debt_sum < s.summ):
                        debt_sum = s.summ
                        drvr_new = s.p1.id
                        pass_new = s.p2.id

            form = TripForm(request.user,
                            initial = {'year':      datetime.now().year,
                                       'week':      week_new,
                                       'days':      0,
                                       'oper':      0,
                                       'price':     price_new,
                                       'driver':    drvr_new,
                                       'passenger': pass_new,
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
    else:
        s = 0
        if (pk != 0):
            t = get_object_or_404(Trip, pk = pk)
            s = t.summa()
        form = TripForm(request.user,
                        request.POST,
                        instance = t,
                        initial = { 'summa': s,
                                    'day_11': request.POST.get('day_11') != None,
                                    'day_12': request.POST.get('day_12') != None,
                                    'day_13': request.POST.get('day_13') != None,
                                    'day_14': request.POST.get('day_14') != None,
                                    'day_15': request.POST.get('day_15') != None,
                                    'day_16': request.POST.get('day_16') != None,
                                    'day_17': request.POST.get('day_17') != None,
                                    'day_21': request.POST.get('day_21') != None,
                                    'day_22': request.POST.get('day_22') != None,
                                    'day_23': request.POST.get('day_23') != None,
                                    'day_24': request.POST.get('day_24') != None,
                                    'day_25': request.POST.get('day_25') != None,
                                    'day_26': request.POST.get('day_26') != None,
                                    'day_27': request.POST.get('day_27') != None,
                                    })
        if form.is_valid():
            if (pk != 0):
                b = Trip.objects.get(id = pk)
                saldo_update(request.user, b.driver, b.passenger, b.oper, -1*b.summa())
            trip = form.save(commit = False)
            trip.user = request.user
            trip.modif = datetime.now()
            trip.save()
            saldo_update(request.user, trip.driver, trip.passenger, trip.oper, trip.summa())
            return HttpResponseRedirect(reverse('trip:trip_list'))

    context = {
        'title': _('trip').capitalize(),
        'site_header': get_current_site(request).name,
        'form': form,
        'trip_id': pk,
        'today': datetime.today().weekday(),
        }
    return render(request, 'trip/trip_form.html', context)

  
def get_day(days, row, col):
    return ((days & (1 << (row-1) + (col-1)*2)) != 0)


def get_me_code(_user):
    try:
        me = Person.objects.get(user = _user, me = 1)
        return me.id
    except Person.DoesNotExist:
        return 0

def saldo_update(_user, _p1, _p2, _oper, _sum):
    if (_p1.id > _p2.id):
        a1 = _p2
        a2 = _p1
        sm = -1*_sum 
    else:
        a1 = _p1
        a2 = _p2
        sm = _sum 
  
    if (_oper == 1):
        sm *= -1
  
    try:
        s = Saldo.objects.get(user = _user.id, p1 = a1.id, p2 = a2.id)
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

def do_count(request):
    Saldo.objects.filter(user = request.user.id).delete()
    trips = Trip.objects.filter(user = request.user.id)
    for t in trips:
        saldo_update(request.user, t.driver, t.passenger, t.oper, t.summa())




