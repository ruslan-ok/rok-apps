from django import forms
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import date, datetime, timedelta
from fuel.models import Fuel, Car, consumption, fuel_summary


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
             'app_text':   'Приложения', 
             'part_text':  'ТО',
             'car_text':   'Авто', 
             'page_title': 'Заправка ' + curcar.name, 
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
        last = Fuel.objects.filter(car = car.id).order_by('-pub_date')[:3]
        new_odo = 0
        new_prc = 0
        new_dat = date.today()

        if (len(last) == 0):
          new_vol = 25
        else:
          new_vol = last[0].volume
          new_prc = last[0].price
          new_dat = last[0].pub_date.date()
          if (len(last) > 2):
            if (last[0].volume != last[1].volume) and (last[1].volume == last[2].volume):
              new_vol = last[1].volume
              new_prc = last[1].price

          cons = consumption(request.user.id)
          if (cons != 0):
            #new_odo = last[0].odometr + int(float(last[0].volume) / cons * 100)
            new_odo = last[0].odometr + int(last[0].volume / cons * 100)

        form = FuelForm(initial={'car': car, 
                                 'pub_date': new_dat.isoformat(),
                                 'odometr': new_odo, 
                                 'volume': new_vol, 'price': new_prc })
      context = edit_context(request, form, car, pk, '')
      return render(request, 'fuel/fuel.html', context)
    else:
      action = request.POST.get('action', False)
      
      act = 0
      if (action == 'Отменить'):
        act = 1
      else:
        if (action == 'Добавить'):
          act = 2
        else:
          if (action == 'Сохранить'):
            act = 3
          else:
            if (action == 'Удалить'):
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
