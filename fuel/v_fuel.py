# coding=UTF-8
from django import forms
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from datetime import date, datetime, timedelta
from fuel.models import Fuel, Car, fuel_summary


debug_text = ''


#============================================================================
class FuelForm(forms.ModelForm):
    class Meta:
        model = Fuel
        exclude = ('car',)

#============================================================================
def edit_context(request, form, car, pid, debug_text):
    fuels = Fuel.objects.filter(car = car).order_by('-pub_date')[:20]
    curcar = Car.objects.get(user = request.user.id, active = 1)
    cars = Car.objects.filter(user = request.user.id, active = 0)
    summary = fuel_summary(request.user.id)
    return { 'form':       form, 
             'fuels':      fuels, 
             'cars':       cars, 
             'pid':        pid, 
             'app_text':   u'Приложения', 
             'part_text':  u'ТО',
             'car_text':   u'Авто', 
             'page_title': u'Заправка ' + curcar.name, 
             'fuels_count':   Fuel.objects.filter(car = car).count,
             'fuel_summary': summary,
             'fuel_status': '',
             'debug_text': debug_text, 
           }
#============================================================================
def do_fuel(request, pk):
    try:
      car = Car.objects.get(user = request.user.id, active = 1)
    except Car.DoesNotExist:
      cars = Car.objects.filter(user = request.user.id, active = 0)
      if (len(cars) == 0):
        car = None
      else:
        car = cars[0]
        car.active = 1
        car.save()
    
    if (car == None):
      return HttpResponseRedirect(reverse('fuel:cars_edit', args=(0,)))

    if (request.method == 'GET'):
      ttt = date.today()
      if (pk > 0):
        # Отображение конкретной записи
        t = get_object_or_404(Fuel, pk=pk)
        ttt = t.pub_date.date()
        form = FuelForm(instance = t,
                        initial={'pub_date': ttt.isoformat()})
      else:
        # Пустая форма для новой записи
        last = Fuel.objects.filter(car = car.id).order_by('-pub_date')[:20]
        qnt = 0
        vol = 0
        prc = 0
        min_odo = 0
        max_odo = 0
        for f in last:
          qnt += 1
          vol += f.volume
          if (prc == 0):
            prc = f.price
          if (f.odometr > max_odo):
            max_odo = f.odometr
          if (f.odometr < min_odo) or (min_odo == 0):
            min_odo = f.odometr
        if (qnt > 1):
          max_odo += (max_odo - min_odo) / (qnt - 1)
          vol = int(round(vol / qnt, -5))
        if (vol == 0):
          vol = 25
        form = FuelForm(initial={'car': car, 
                                 'pub_date': date.today().isoformat(), 
                                 'odometr': max_odo, 
                                 'volume': vol, 'price': prc })
      context = edit_context(request, form, car, pk, ttt.isoformat())
      return render(request, 'fuel/fuel.html', context)
    else:
      action = request.POST.get('action', False)
      
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
        form = FuelForm(request.POST)
        if not form.is_valid():
          # Ошибки в форме, отобразить её снова
          context = edit_context(request, form, car, pk, 'post-error' + str(form.non_field_errors))
          return render(request, 'fuel/fuel.html', context)
        else:
          t = form.save(commit=False)
    
          if (act == 2):
            t.car = car
            t.pub_date = t.pub_date + timedelta(days=1)
            t.save()
    
          if (act == 3):
            t.id = pk
            t.car = car
            t.pub_date = t.pub_date + timedelta(days=1)
            t.save()
    
          if (act == 4):
            t = get_object_or_404(Fuel, id=pk)
            t.delete()
    
      return HttpResponseRedirect(reverse('fuel:fuel_view'))

def do_change_car(request, pk):
    active_cars = Car.objects.filter(user = request.user.id, active = 1)
    for c in active_cars:
      c.active = 0
      c.save()
    car = Car.objects.get(id = pk)
    car.active = 1
    car.save()
    return HttpResponseRedirect(reverse('fuel:fuel_view'))
