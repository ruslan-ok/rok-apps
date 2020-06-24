from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from hier.utils import get_base_context, get_folder_id, process_common_commands
from .models import Car, deactivate_all, set_active, Fuel, Part
from .forms import CarForm


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def cars_list(request):
    process_common_commands(request)
    data = Car.objects.filter(user = request.user.id).order_by('name')
    if request.method != 'GET':
        page_number = 1
    else:
        page_number = request.GET.get('page')
    paginator = Paginator(data, 20)
    page_obj = paginator.get_page(page_number)
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, 0, _('cars'), 'content_list')
    context['page_obj'] = page_obj
    template_file = 'fuel/cars_list.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

#----------------------------------
def cars_add(request):
    if (request.method == 'POST'):
        form = CarForm(request.POST)
    else:
        form = CarForm(initial = { 'name': '', 'plate': '', 'active': False })
    return show_page_form(request, 0, _('creating a new car'), form)

#----------------------------------
def cars_form(request, pk):
    data = get_object_or_404(Car.objects.filter(id = pk, user = request.user.id))
    if (request.method == 'POST'):
        form = CarForm(request.POST, instance = data)
    else:
        form = CarForm(instance = data)
    return show_page_form(request, pk, _('car') + ' "' + data.name + '"', form)

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def cars_del(request, pk):
    car = get_object_or_404(Car.objects.filter(id = pk, user = request.user.id))
    if Fuel.objects.filter(car = car.id).exists() or Part.objects.filter(car = car.id).exists():
        set_active(request.user.id, car.id)
        return HttpResponseRedirect(reverse('fuel:cars_list'))

    if car.active:
        if Car.objects.filter(user = request.user.id).exclude(id = car.id).exists():
            new_active = Car.objects.filter(user = request.user.id).exclude(id = car.id)[0]
            set_active(request.user.id, new_active.id)

    car.delete()
    return HttpResponseRedirect(reverse('fuel:cars_list'))


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def show_page_form(request, pk, title, form):
    if (request.method == 'POST'):
        if form.is_valid():
            data = form.save(commit = False)
            if data.active:
                deactivate_all(request.user.id, data.id)
            data.user = request.user
            form.save()
            return HttpResponseRedirect(reverse('fuel:cars_list'))
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, pk, title, form = form)
    template = loader.get_template('fuel/cars_form.html')
    return HttpResponse(template.render(context, request))
