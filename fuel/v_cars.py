from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
from django.forms import ModelForm
from hier.utils import get_base_context
from .models import Car


class CarsForm(ModelForm):
    action = forms.CharField(widget = forms.HiddenInput, required = False)
    active = forms.IntegerField(label = 'Активная', required = False)

    class Meta:
        model = Car
        fields = ('name', 'plate', 'active', 'action')

#============================================================================
def edit_context(_request, _form, fl, _pid, _debug_text):
    cars = Car.objects.filter(user = _request.user.id)
    context = get_base_context(_request, fl, _pid, 'Автомобили', 'fuel')
    context['cars'] =  cars 
    context['form'] =  _form 
    context['app_text'] =  'Приложения' 
    context['fuel_text'] =  'Заправка' 
    context['page_title'] =  'Автомобили' 
    context['debug_text'] =  _debug_text
    return context

#============================================================================
def do_cars(request, fl, pk):
  if (request.method == 'GET'):
    if (pk > 0):
      t = get_object_or_404(Car, pk=pk)
      form = CarsForm(instance = t)
    else:
      form = CarsForm(initial = {'name': '', 'plate': '', 'active': 0})
    context = edit_context(request, form, fl, pk, 'get-1')
    return render(request, 'fuel/cars.html', context)
  else:
    action = request.POST.get('action', False)
    active = request.POST.get('active', False)
    
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
      form = CarsForm(request.POST)
      if not form.is_valid():
        # Ошибки в форме, отобразить её снова
        context = edit_context(request, form, fl, pk, 'post-error' + str(form.non_field_errors))
        return render(request, 'fuel/cars.html', context)
      else:
        t = form.save(commit=False)

        if (act < 4):
          if (int(active) > 0):
            active_cars = Car.objects.filter(user = request.user.id, active = 1)
            for c in active_cars:
              c.active = 0
              c.save()

        if (act == 2):
          t.user = request.user
          t.active = int(active)
          t.save()

        if (act == 3):
          t.id = pk
          t.user = request.user
          t.active = int(active)
          t.save()

        if (act == 4):
          t = get_object_or_404(Car, id=pk)
          t.delete()

    return HttpResponseRedirect(reverse('fuel:cars_view', args = [fl]))

