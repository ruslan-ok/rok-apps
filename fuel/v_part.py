from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from datetime import date, datetime, timedelta
from hier.utils import get_base_context
from .models import Fuel, Car, Part


debug_text = ''


#============================================================================
class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        exclude = ('car',)

#============================================================================
def edit_context(request, form, car, pid, _last_date, _last_odo, debug_text):
    car = Car.objects.get(id = car)
    parts = Part.objects.filter(car = car)
    fuel_odo  = 0
    fuel_date = date.min.isoformat()
    fuel = Fuel.objects.filter(car = car).order_by('-pub_date')[:1]
    if (len(fuel) == 1):
      fuel_odo  = fuel[0].odometr
      fuel_date = date(fuel[0].pub_date.year, fuel[0].pub_date.month, fuel[0].pub_date.day).isoformat()
    s_last_date = ''
    if (_last_date != date.min):
      s_last_date = _last_date.strftime('%d.%m.%Y')
    context = get_base_context(request, 0, 0, 'Список расходников ' + car.name, 'fuel')
    context['form'] =        form 
    context['parts'] =       parts 
    context['pid'] =         pid 
    context['last_date'] =   s_last_date
    context['last_odo'] =    _last_odo
    context['fuel_date'] =   fuel_date
    context['fuel_odo'] =    fuel_odo
    context['app_text'] =    'Приложения' 
    context['page_title'] =  'Список расходников ' + car.name 
    context['fuel_text'] =   'Заправки' 
    context['debug_text'] =  debug_text 
    return context

#============================================================================
def do_part(request, pk):
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
      return HttpResponseRedirect(reverse('fuel:part_view', args=()))

    if (request.method == 'GET'):
      if (pk > 0):
        # Отображение конкретной записи
        t = get_object_or_404(Part, pk=pk)
        form = PartForm(instance = t)
        context = edit_context(request, form, car.id, pk, t.last_date(), t.last_odo(), '')
      else:
        # Пустая форма для новой записи
        form = PartForm(initial={'car': car, 'name': '', 'comment': ''})
        context = edit_context(request, form, car.id, pk, date.min, 0, '')
      return render(request, 'fuel/part.html', context)
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
        form = PartForm(request.POST)
        if not form.is_valid():
          # Ошибки в форме, отобразить её снова
          context = edit_context(request, form, car.id, pk, date.min, 0, 'post-error' + str(form.non_field_errors))
          return render(request, 'fuel/part.html', context)
        else:
          t = form.save(commit = False)
    
          if (act == 2):
            t.car = car
            if (t.chg_km == None):
              t.chg_km = 0
            if (t.chg_mo == None):
              t.chg_mo = 0
            t.save()
    
          if (act == 3):
            t.id = pk
            t.car = car
            if (t.chg_km == None):
              t.chg_km = 0
            if (t.chg_mo == None):
              t.chg_mo = 0
            t.save()
    
          if (act == 4):
            t = get_object_or_404(Part, id=pk)
            t.delete()
    
      return HttpResponseRedirect(reverse('fuel:part_view'))
