from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from hier.utils import get_base_context, get_folder_id
from .models import Car, Fuel, consumption
from .forms import FuelForm


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def fuel_list(request):
    if not Car.objects.filter(user = request.user.id, active = True).exists():
        return HttpResponseRedirect(reverse('fuel:cars_list'))

    car = Car.objects.filter(user = request.user.id, active = True).get()
    data = Fuel.objects.filter(car = car.id).order_by('-pub_date')
    if request.method != 'GET':
        page_number = 1
    else:
        page_number = request.GET.get('page')
    paginator = Paginator(data, 20)
    page_obj = paginator.get_page(page_number)
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, 0, _('refuels') + ' ' + car.name, 'content_list')
    context['page_obj'] = page_obj
    template_file = 'fuel/fuel_list.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

#----------------------------------
def fuel_add(request):
    if (request.method == 'POST'):
        form = FuelForm(request.POST)
    else:
        car = get_object_or_404(Car.objects.filter(user = request.user.id, active = True))
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

          cons = consumption(request.user.id)
          if (cons != 0):
            new_odo = last[0].odometr + int(last[0].volume / cons * 100)

        form = FuelForm(initial = { 'pub_date': datetime.now(), 'odometr': new_odo, 'volume': new_vol, 'price': new_prc })
    return show_page_form(request, 0, _('creating a new refuel') + ' ' + car.name, form)

#----------------------------------
def fuel_form(request, pk):
    car = get_object_or_404(Car.objects.filter(user = request.user.id, active = True))
    data = get_object_or_404(Fuel.objects.filter(id = pk, car = car.id))
    if (request.method == 'POST'):
        form = FuelForm(request.POST, instance = data)
    else:
        form = FuelForm(instance = data)
    return show_page_form(request, pk, _('refuel') + ' ' + car.name, form)

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def fuel_del(request, pk):
    car = get_object_or_404(Car.objects.filter(user = request.user.id, active = True))
    refuel = get_object_or_404(Fuel.objects.filter(id = pk, car = car.id))
    refuel.delete()
    return HttpResponseRedirect(reverse('fuel:fuel_list'))


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def show_page_form(request, pk, title, form):
    car = get_object_or_404(Car.objects.filter(user = request.user.id, active = True))
    if (request.method == 'POST'):
        if form.is_valid():
            data = form.save(commit = False)
            data.car = car
            form.save()
            return HttpResponseRedirect(reverse('fuel:fuel_list'))
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, pk, title)
    context['form'] = form
    template = loader.get_template('fuel/fuel_form.html')
    return HttpResponse(template.render(context, request))
