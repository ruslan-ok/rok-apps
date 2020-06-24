from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from hier.models import Folder
from hier.utils import get_base_context, get_folder_id, process_common_commands
from .utils import next_period
from .models import Apart, Meter
from .forms import MeterForm


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def meter_list(request):
    process_common_commands(request)
    if not Apart.objects.filter(user = request.user.id, active = True).exists():
        return HttpResponseRedirect(reverse('apart:apart_list'))
    apart = Apart.objects.filter(user = request.user.id, active = True)[0]
    data = Meter.objects.filter(apart = apart.id).order_by('-period')
    if request.method != 'GET':
        page_number = 1
    else:
        page_number = request.GET.get('page')
    paginator = Paginator(data, 10)
    page_obj = paginator.get_page(page_number)
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, 0, _('meters'), 'content_list')
    context['page_obj'] = page_obj
    context['apart'] = apart
    template_file = 'apart/meter_list.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

#----------------------------------
def meter_add(request):
    apart = get_object_or_404(Apart.objects.filter(user = request.user.id, active = True))
    if (request.method == 'POST'):
        form = MeterForm(request.POST)
    else:
        qty = len(Meter.objects.filter(apart = apart.id))
        if (qty == 0):
            period = next_period()
            el = 0
            hw = 0
            cw = 0
            ga = 0
        else:
            last = Meter.objects.filter(apart = apart.id).order_by('-period')[0]
            period = next_period(last.period)

            el = last.el
            hw = last.hw
            cw = last.cw
            ga = last.ga

            if (qty > 1):
                first = Meter.objects.filter(apart = apart.id).order_by('period')[0]
                el = last.el + round((last.el - first.el) / (qty - 1))
                hw = last.hw + round((last.hw - first.hw) / (qty - 1))
                cw = last.cw + round((last.cw - first.cw) / (qty - 1))
                ga = last.ga + round((last.ga - first.ga) / (qty - 1))

        form = MeterForm(initial = { 'period': period, 'reading': datetime.now(), 'el': el, 'hw': hw, 'cw': cw, 'ga': ga })

    return show_page_form(request, 0, _('adding new meter readings'), form, apart)

#----------------------------------
def meter_form(request, pk):
    apart = get_object_or_404(Apart.objects.filter(user = request.user.id, active = True))
    data = get_object_or_404(Meter.objects.filter(apart = apart.id, id = pk))
    if (request.method == 'POST'):
        form = MeterForm(request.POST, instance = data)
    else:
        form = MeterForm(instance = data)
    return show_page_form(request, pk, _('meter readings from ') + data.period.strftime('%m.%Y'), form, apart)

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def meter_del(request, pk):
    apart = get_object_or_404(Apart.objects.filter(user = request.user.id, active = True))
    meter = get_object_or_404(Meter.objects.filter(apart = apart.id, id = pk))
    meter.delete()
    return HttpResponseRedirect(reverse('apart:meter_list'))


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def show_page_form(request, pk, title, form, apart):
    if (request.method == 'POST'):
        if form.is_valid():
            data = form.save(commit = False)
            data.apart = apart
            form.save()
            return HttpResponseRedirect(reverse('apart:meter_list'))
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, pk, title, form = form)
    context['apart'] = apart
    template = loader.get_template('apart/meter_form.html')
    return HttpResponse(template.render(context, request))
