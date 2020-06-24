from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from hier.utils import get_base_context, get_folder_id, process_common_commands
from .models import Car, Fuel, Repl, Part, init_repl_car
from .forms import ReplForm


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def repl_list(request):
    process_common_commands(request)
    if not Car.objects.filter(user = request.user.id, active = True).exists():
        return HttpResponseRedirect(reverse('fuel:cars_list'))

    if Repl.objects.filter(car__isnull = True).exists():
        init_repl_car()
    
    car = Car.objects.filter(user = request.user.id, active = True).get()

    data = Repl.objects.filter(car = car.id).order_by('-dt_chg')
    if request.method != 'GET':
        page_number = 1
    else:
        page_number = request.GET.get('page')
    paginator = Paginator(data, 20)
    page_obj = paginator.get_page(page_number)
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, 0, _('replacements') + ' ' + car.name, 'content_list')
    context['page_obj'] = page_obj
    template_file = 'fuel/repl_list.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

#----------------------------------
def repl_add(request):
    car = get_object_or_404(Car.objects.filter(user = request.user.id, active = True))
    if (request.method == 'POST'):
        form = ReplForm(request.POST)
    else:
        last = Fuel.objects.filter(car = car.id).order_by('-pub_date')[:1]
        new_odo = 0

        if (len(last) != 0):
          new_odo = last[0].odometr

        new_part = None

        form = ReplForm(initial = { 'part': new_part, 'dt_chg': datetime.now(), 'odometr': new_odo, 'name': '', 'manuf': '', 'part_num': '', 'comment': '' })
    return show_page_form(request, 0, _('creating a new replacement') + ' ' + car.name, form)

#----------------------------------
def repl_form(request, pk):
    car = get_object_or_404(Car.objects.filter(user = request.user.id, active = True))
    data = get_object_or_404(Repl.objects.filter(id = pk, car = car.id))
    if (request.method == 'POST'):
        form = ReplForm(request.POST, instance = data)
    else:
        form = ReplForm(instance = data)
    return show_page_form(request, pk, _('replacement') + ' ' + car.name, form)

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def repl_del(request, pk):
    car = get_object_or_404(Car.objects.filter(user = request.user.id, active = True))
    repl = get_object_or_404(Repl.objects.filter(id = pk, car = car.id))
    repl.delete()
    return HttpResponseRedirect(reverse('fuel:repl_list'))


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
            return HttpResponseRedirect(reverse('fuel:repl_list'))
    form.fields['part'].queryset = Part.objects.filter(car = car.id).order_by('name')
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, pk, title, form = form)
    template = loader.get_template('fuel/repl_form.html')
    return HttpResponse(template.render(context, request))
