from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from hier.models import Folder
from hier.utils import get_base_context, get_folder_id
from .utils import next_period
from .models import Apart, Meter, Bill, get_price_info, count_by_tarif, ELECTRICITY, GAS, WATER
from .forms import BillForm


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def bill_list(request):
    if not Apart.objects.filter(user = request.user.id, active = True).exists():
        return HttpResponseRedirect(reverse('apart:apart_list'))
    apart = get_object_or_404(Apart.objects.filter(user = request.user.id, active = True))
    data = Bill.objects.filter(apart = apart.id).order_by('-period')
    if request.method != 'GET':
        page_number = 1
    else:
        page_number = request.GET.get('page')
    paginator = Paginator(data, 10)
    page_obj = paginator.get_page(page_number)
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, 0, _('bills'), 'content_list')
    context['page_obj'] = page_obj
    template_file = 'apart/bill_list.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

#----------------------------------
def bill_add(request):
    apart = get_object_or_404(Apart.objects.filter(user = request.user.id, active = True))
    
    if (len(Meter.objects.filter(apart = apart.id)) < 2):
        # Нет показаний счетчиков
        return HttpResponseRedirect(reverse('apart:meter_list'))

    if (request.method == 'POST'):
        form = BillForm(request.POST)
        prev_id = request.POST['prev_id']
        curr_id = request.POST['curr_id']
        prev = Meter.objects.filter(apart = apart.id, id = prev_id).get()
        curr = Meter.objects.filter(apart = apart.id, id = curr_id).get()
    else:
        if not Bill.objects.filter(apart = apart.id).exists():
            # Первая оплата
            prev = Meter.objects.filter(apart = apart.id).order_by('period')[0]
            curr = Meter.objects.filter(apart = apart.id).order_by('period')[1]
            period = curr.period
        else:
            last = Bill.objects.filter(apart = apart.id).order_by('-period')[0]
            period = next_period(last.period)
            if not Meter.objects.filter(apart = apart.id, period = period).exists(): 
                # Нет показаний счетчиков для очередного периода
                return HttpResponseRedirect(reverse('apart:meter_list'))
            prev = last.curr
            curr = Meter.objects.filter(apart = apart.id, period = period).get()

        form = BillForm(initial = { 'period': period, 'payment': datetime.now() })

    return show_page_form(request, 0, _('create a new bill'), form, apart, prev, curr)

#----------------------------------
def bill_form(request, pk):
    apart = get_object_or_404(Apart.objects.filter(user = request.user.id, active = True))
    data = get_object_or_404(Bill.objects.filter(id = pk, apart = apart.id))
    if (request.method == 'POST'):
        form = BillForm(request.POST, instance = data)
    else:
        form = BillForm(instance = data)
    return show_page_form(request, pk, _('bill from ') + data.period.strftime('%m.%Y'), form, apart, data.prev, data.curr)

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def bill_del(request, pk):
    apart = get_object_or_404(Apart.objects.filter(user = request.user.id, active = True))
    data = get_object_or_404(Bill.objects.filter(id = pk, apart = apart.id))
    data.delete()
    return HttpResponseRedirect(reverse('apart:bill_list'))


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def show_page_form(request, pk, title, form, apart, prev, curr):
    if (request.method == 'POST'):
        if form.is_valid():
            data = form.save(commit = False)
            data.apart = apart
            data.prev = prev
            data.curr = curr
            form.save()
            return HttpResponseRedirect(reverse('apart:bill_list'))

    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, pk, title)
    context['period_num'] = form.instance.period.year * 100 + form.instance.period.month
    context['form'] = form
    context['apart'] = apart
    context['prev'] = prev
    context['curr'] = curr
    context['volume'] = { 'el': curr.el - prev.el,
                          'ga': curr.ga - prev.ga,
                          'wt': (curr.hw + curr.cw) - (prev.hw + prev.cw) }
    context['el_tar'] = get_price_info(request.user.id, ELECTRICITY, curr.period.year, curr.period.month)
    context['gas_tar'] = get_price_info(request.user.id, GAS, curr.period.year, curr.period.month)
    context['water_tar'] = get_price_info(request.user.id, WATER, curr.period.year, curr.period.month)
    context['el_bill'] = count_by_tarif(request.user.id, prev, curr, ELECTRICITY)
    context['gas_bill'] = count_by_tarif(request.user.id, prev, curr, GAS)
    context['water_bill'] = count_by_tarif(request.user.id, prev, curr, WATER)
    
    template = loader.get_template('apart/bill_form.html')
    return HttpResponse(template.render(context, request))
