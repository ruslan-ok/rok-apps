from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from hier.utils import get_base_context, process_common_commands, get_param, set_article, save_last_visited
from .models import Apart, Meter, Bill, enrich_context, get_price_info, count_by_tarif, ELECTRICITY, GAS, WATER
from .forms import BillForm
from .utils import next_period

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def bill_list(request):
    if process_common_commands(request):
        return HttpResponseRedirect(reverse('apart:bill_list'))

    if not Apart.objects.filter(user = request.user.id, active = True).exists():
        return HttpResponseRedirect(reverse('apart:apart_list'))
    apart = get_object_or_404(Apart.objects.filter(user = request.user.id, active = True))
    data = Bill.objects.filter(apart = apart.id).order_by('-period')

    param = get_param(request.user, 'apart:bill')

    if param.article and Bill.objects.filter(apart = apart.id, id = param.article_pk).exists():
        bill = Bill.objects.filter(apart = apart.id, id = param.article_pk).get()
        title = '{} {} {} {}'.format(_('bill in').capitalize(), apart.name, _('for the period'), bill.period.strftime('%m.%Y'))
    else:
        title = '{} {}'.format(_('bills in').capitalize(), apart.name)

    if (request.method == 'POST'):
        if ('item-add' in request.POST):
            bill = bill_add(request, apart)
            if not bill:
                return HttpResponseRedirect(reverse('apart:meter_list'))
            set_article(request.user, 'apart:bill', bill.id)
            return HttpResponseRedirect(reverse('apart:bill_form', args = [bill.id]))

    context = get_base_context(request, 0, 0, title, 'content_list', make_tree = False, article_enabled = True)
    save_last_visited(request.user, 'apart:bill_list', 'apart', context['title'])

    redirect = False
    if param.article:
        if Bill.objects.filter(id = param.article_pk, apart = apart.id).exists():
            redirect = get_bill_article(request, context, param.article_pk)
        else:
            set_article(request.user, '', 0)
            redirect = True
    
    if redirect:
        return HttpResponseRedirect(reverse('apart:bill_list'))

    enrich_context(context, param, request.user.id)
    page_number = 1
    if (request.method == 'GET'):
        page_number = request.GET.get('page')
    paginator = Paginator(data, 10)
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = paginator.get_page(page_number)

    template_file = 'apart/bill_form.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def bill_form(request, pk):
    set_article(request.user, 'apart:bill', pk)
    return HttpResponseRedirect(reverse('apart:bill_list'))

#----------------------------------
def bill_add(request, apart):
    if (len(Meter.objects.filter(apart = apart.id)) < 2):
        # Нет показаний счетчиков
        return None

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
            return None
        prev = last.curr
        curr = Meter.objects.filter(apart = apart.id, period = period).get()

    form = BillForm(initial = { 'period': period, 'payment': datetime.now() })

    bill = Bill.objects.create(apart = apart, period = period, payment = datetime.now(), prev = prev, curr = curr)
    return bill


#----------------------------------
def get_bill_article(request, context, pk):
    ed_bill = get_object_or_404(Bill.objects.filter(id = pk))
    form = None
    if (request.method == 'POST'):
        if ('article_delete' in request.POST):
            ed_bill.delete()
            set_article(request.user, '', 0)
            return HttpResponseRedirect(reverse('apart:bill_list'))
        if ('bill-save' in request.POST):
            form = BillForm(request.POST, instance = ed_bill)
            if form.is_valid():
                data = form.save(commit = False)
                form.save()
                return True

    if not form:
        form = BillForm(instance = ed_bill)

    context['form'] = form
    context['item_id'] = ed_bill.id
    context['period_num'] = form.instance.period.year * 100 + form.instance.period.month
    context['apart'] = ed_bill.apart
    prev = ed_bill.prev
    curr = ed_bill.curr
    context['prev'] = prev
    context['curr'] = curr
    context['volume'] = { 'el': curr.el - prev.el,
                          'ga': curr.ga - prev.ga,
                          'wt': (curr.hw + curr.cw) - (prev.hw + prev.cw) }
    context['el_tar'] = get_price_info(ed_bill.apart.id, ELECTRICITY, curr.period.year, curr.period.month)
    context['gas_tar'] = get_price_info(ed_bill.apart.id, GAS, curr.period.year, curr.period.month)
    context['water_tar'] = get_price_info(ed_bill.apart.id, WATER, curr.period.year, curr.period.month)
    context['el_bill'] = count_by_tarif(ed_bill.apart.id, prev, curr, ELECTRICITY)
    context['gas_bill'] = count_by_tarif(ed_bill.apart.id, prev, curr, GAS)
    context['water_bill'] = count_by_tarif(ed_bill.apart.id, prev, curr, WATER)
    return False



