from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from hier.utils import get_base_context, get_folder_id, process_common_commands
from .models import Car, Part
from .forms import PartForm


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def part_list(request):
    process_common_commands(request)
    if not Car.objects.filter(user = request.user.id, active = True).exists():
        return HttpResponseRedirect(reverse('fuel:cars_list'))

    car = Car.objects.filter(user = request.user.id, active = True).get()
    data = Part.objects.filter(car = car.id).order_by('name')
    if request.method != 'GET':
        page_number = 1
    else:
        page_number = request.GET.get('page')
    paginator = Paginator(data, 20)
    page_obj = paginator.get_page(page_number)
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, 0, _('parts') + ' ' + car.name, 'content_list')
    context['page_obj'] = page_obj
    template_file = 'fuel/part_list.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

#----------------------------------
def part_add(request):
    if (request.method == 'POST'):
        form = PartForm(request.POST)
    else:
        form = PartForm(initial = { 'name': '', 'chg_km': 0, 'chg_mo': 0 })
    return show_page_form(request, 0, _('creating a new part') + ' ' + car.name, form)

#----------------------------------
def part_form(request, pk):
    car = get_object_or_404(Car.objects.filter(user = request.user.id, active = True))
    data = get_object_or_404(Part.objects.filter(id = pk, car = car.id))
    if (request.method == 'POST'):
        form = PartForm(request.POST, instance = data)
    else:
        form = PartForm(instance = data)
    return show_page_form(request, pk, _('part') + ' "' + data.name + '" ' + car.name, form)

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def part_del(request, pk):
    car = get_object_or_404(Car.objects.filter(user = request.user.id, active = True))
    part = get_object_or_404(Part.objects.filter(id = pk, car = car.id))
    if Repl.objects.filter(part = part.id).exists():
        return HttpResponseRedirect(reverse('fuel:part_list'))

    part.delete()
    return HttpResponseRedirect(reverse('fuel:part_list'))


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
            return HttpResponseRedirect(reverse('fuel:part_list'))
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, pk, title, form = form)
    template = loader.get_template('fuel/part_form.html')
    return HttpResponse(template.render(context, request))
