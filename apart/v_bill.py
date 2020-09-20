import os
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from hier.utils import get_base_context_ext, process_common_commands, get_rate_on_date, extract_get_params
from hier.params import set_article_visible, set_article_kind
from hier.files import file_storage_path, get_files_list
from .models import app_name, Apart, Meter, Bill, enrich_context, get_price_info, count_by_tarif, ELECTRICITY, GAS, WATER
from .forms import BillForm, FileForm
from .utils import next_period

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def bill_list(request):
    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('apart:bill_list'))

    if not Apart.objects.filter(user = request.user.id, active = True).exists():
        return HttpResponseRedirect(reverse('apart:apart_list'))
    apart = get_object_or_404(Apart.objects.filter(user = request.user.id, active = True))
    data = Bill.objects.filter(apart = apart.id).order_by('-period')

    if (request.method == 'POST'):
        if ('item-add' in request.POST):
            bill = bill_add(request, apart)
            if not bill:
                return HttpResponseRedirect(reverse('apart:meter_list'))
            return HttpResponseRedirect(reverse('apart:bill_form', args = [bill.id]))

    title = '{} [{}]'.format(_('bills').capitalize(), apart.name)
    app_param, context = get_base_context_ext(request, app_name, 'bill', title)

    redirect = False
    
    if app_param.article:
        if (app_param.kind != 'bill'):
            set_article_visible(request.user, app_name, False)
            redirect = True
        elif Bill.objects.filter(id = app_param.art_id, apart = apart.id).exists():
            redirect = get_bill_article(request, context, app_param.art_id)
        else:
            set_article_visible(request.user, app_name, False)
            redirect = True
    
    if redirect:
        return HttpResponseRedirect(reverse('apart:bill_list'))

    enrich_context(context, app_param, request.user.id)
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
    set_article_kind(request.user, app_name, 'bill', pk)
    return HttpResponseRedirect(reverse('apart:bill_list') + extract_get_params(request))

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

    rate = get_rate_on_date(145, datetime.now())
    bill = Bill.objects.create(apart = apart, period = period, payment = datetime.now(), prev = prev, curr = curr, rate = rate)
    return bill


#----------------------------------
def get_bill_article(request, context, pk):
    ed_bill = get_object_or_404(Bill.objects.filter(id = pk))
    form = None
    if (request.method == 'POST'):
        if ('article_delete' in request.POST):
            if not Bill.objects.filter(period__gt = ed_bill.period).exists():
                ed_bill.delete()
                set_article_visible(request.user, app_name, False)
            return HttpResponseRedirect(reverse('apart:bill_list'))
        if ('bill-save' in request.POST):
            form = BillForm(request.POST, instance = ed_bill)
            if form.is_valid():
                data = form.save(commit = False)
                data.rate = get_rate_on_date(145, data.payment)
                form.save()
                return True
        if ('url-delete' in request.POST):
            ed_bill.url = ''
            ed_bill.save()
            return True
        if ('file-upload' in request.POST):
            file_form = FileForm(request.POST, request.FILES)
            if file_form.is_valid():
                handle_uploaded_file(request.FILES['upload'], request.user, ed_bill)
                return True

    if not form:
        form = BillForm(instance = ed_bill)

    context['form'] = form
    context['item_id'] = ed_bill.id
    context['bill_period'] = ed_bill.period
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
    context['url_cutted'] = ed_bill.url
    if (len(ed_bill.url) > 50):
        context['url_cutted'] = ed_bill.url[:50] + '...'
    context['files'] = get_files_list(request.user, app_name, 'apart_{0}/{1}/{2}'.format(ed_bill.apart.id, ed_bill.period.year, str(ed_bill.period.month).zfill(2)))
    return False


def get_file_storage_path(user, bill):
    return file_storage_path.format(user.id) + '{0}/apart_{1}/{2}/{3}/'.format(app_name, bill.apart.id, bill.period.year, str(bill.period.month).zfill(2))

def handle_uploaded_file(f, user, bill):
    path = get_file_storage_path(user, bill)
    os.makedirs(os.path.dirname(path), exist_ok = True)
    with open(path + f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def get_doc(request, name):
    app_param, context = get_base_context_ext(request, app_name, 'bill', '')
    bill = get_object_or_404(Bill.objects.filter(id = app_param.art_id))
    path = get_file_storage_path(request.user, bill)
    try:
        fsock = open(path + name, 'rb')
        return FileResponse(fsock)
    except IOError:
        response = HttpResponseNotFound()


