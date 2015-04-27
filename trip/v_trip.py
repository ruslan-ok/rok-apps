# coding=UTF-8
from datetime import datetime, date
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django import forms
from django.forms import ModelForm
from trip.models import Person, Saldo, Trip, trip_summary


#============================================================================
class TripForm(ModelForm):
    days = forms.IntegerField(u'Дни', required = False)
    class Meta:
        model = Trip
        exclude = ('user',)

#============================================================================
def edit_context(_request, _form, _pid, _debug_text, _debt_sum, _last_prc):
    persons = Person.objects.filter(user = _request.user.id)
    trips = Trip.objects.filter(user = _request.user.id).order_by('-year', '-week', '-oper')[:20]
    return {
      'app_text':       u'Приложения',
      'count_text':     u'Пересчитать',
      'pers_text':      u'Люди',
      'week_text':      u'Выходные',
      'page_title':     u'Проезд',
      'trip_summary':   trip_summary(_request.user.id),
      'trip_status':    '',
      'form':           _form,
      'pid':            _pid,
      'oper_trip':      u'проезд',
      'oper_pay':       u'оплата',
      'trips':          trips,
      'trips_count':    Trip.objects.filter(user = _request.user.id).count,
      'persons':        persons,
      'debt':           _debt_sum,
      'last_prc':       _last_prc,
      'debug_text':     _debug_text
      }


def get_trip_new(request):
    # Инициализация полей новой записи
    last_trip = Trip.objects.filter(user = request.user.id, oper = 0).order_by('-year', '-week', '-days')[:1]
    price_new  = 0
    drvr_new = 2
    pass_new = 1
    debt_sum = 0

    if (len(last_trip) > 0): # последняя поездка
      price_new  = last_trip[0].price
      drvr_new   = last_trip[0].driver.id
      pass_new   = last_trip[0].passenger.id

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

    form = TripForm(initial = {'year':      datetime.now().year,
                               'week':      int(datetime.now().strftime("%j")) / 7 + 1,
                               'days':      0,
                               'oper':      0,
                               'price':     price_new,
                               'driver':    drvr_new,
                               'passenger': pass_new,
                               'text':      '' })
    context = edit_context(request, form, 0, 'get-1', debt_sum, price_new)
    return render(request, 'trip/trip.html', context)

def do_trip(request, pk):
  if (request.method == 'GET'):
    if (pk == 0):
      return get_trip_new(request)
    else:
      t = get_object_or_404(Trip, pk=pk)
      form = TripForm(instance = t)
      context = edit_context(request, form, pk, 'get-1', 0, t.price)
      return render(request, 'trip/trip.html', context)
  else:
    action = request.POST.get('action', False)
    days   = request.POST.get('ret_days', False)
    
    act = 0
    if (action == u'Отменить'):
      act = 1
    else:
      if (action == u'Добавить'):
        act = 2
      else:
        if (action == u'Сохранить'):
          act = 3
        else:
          if (action == u'Удалить'):
            act = 4
          else:
            act = 5

    if (act > 1):
      form = TripForm(request.POST)
      if not form.is_valid():
        # Ошибки в форме, отобразить её снова
        context = edit_context(request, form, pk, 'post-error' + str(form.non_field_errors), 0, int(request.POST.get('last_prc', False)))
        return render(request, 'trip/trip.html', context)
      else:
        t = form.save(commit=False)

        if (act == 2):
          t.user = request.user
          t.days = days
          #t.text = 'act = 2, driver = ' + str(t.driver) + ', passenger = ' + str(t.passenger) + ', summa = ' + str(t.summa())
          t.save()
          saldo_update(request.user, t.driver, t.passenger, t.oper, t.summa())

        if (act == 3):
          b = Trip.objects.get(id = pk)
          saldo_update(request.user, b.driver, b.passenger, b.oper, -1*b.summa())
          t.id = pk
          t.user = request.user
          t.days = days
          #t.text = 'act = 3, driver = ' + str(t.driver) + ', passenger = ' + str(t.passenger) + ', summa = ' + str(t.summa())
          t.save()
          saldo_update(request.user, t.driver, t.passenger, t.oper, t.summa())

        if (act == 4):
          t = get_object_or_404(Trip, id=pk)
          saldo_update(request.user, t.driver, t.passenger, t.oper, -1*t.summa())
          t.delete()

    return HttpResponseRedirect(reverse('trip:trip_view'))

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




