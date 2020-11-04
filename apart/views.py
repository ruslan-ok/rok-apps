import os, locale
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, HttpResponseNotFound
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q

from hier.utils import get_base_context_ext, process_common_commands, extract_get_params, sort_data
from hier.params import set_sort_mode, toggle_sort_dir, get_search_mode, get_search_info, set_restriction, set_article_kind, set_article_visible
from hier.models import get_app_params, toggle_content_group
from hier.aside import Fix, Sort
from hier.content import find_group
from hier.files import storage_path, get_files_list
from todo.utils import nice_date
from .models import app_name, Apart, Service, Meter, Bill, Price, set_active, get_price_info, count_by_tarif, ELECTRICITY, GAS, WATER
from .forms import ApartForm, ServiceForm, MeterForm, BillForm, PriceForm, FileForm
from .utils import next_period

items_per_page = 10

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def main(request):
    app_param = get_app_params(request.user, app_name)
    if (app_param.restriction != 'apart') and (app_param.restriction != 'meter') and (app_param.restriction != 'price') and (app_param.restriction != 'bill') and (app_param.restriction != 'service'):
        set_restriction(request.user, app_name, 'bill')
        return HttpResponseRedirect(reverse('apart:main') + extract_get_params(request))

    if not Apart.objects.filter(user = request.user.id, active = True).exists():
        if (app_param.restriction != 'apart'):
            set_restriction(request.user, app_name, 'apart')
            return HttpResponseRedirect(reverse('apart:main'))

    apart = Apart.objects.filter(user = request.user.id, active = True).get()

    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('apart:main') + extract_get_params(request))

    # для трансляции строкового представления дат, в частности в item_info
    locale.setlocale(locale.LC_CTYPE, request.LANGUAGE_CODE)
    locale.setlocale(locale.LC_TIME, request.LANGUAGE_CODE)

    form = None
    if (request.method == 'POST'):
        #raise Exception(request.POST)
        if ('item-add' in request.POST):
            if (app_param.restriction == 'apart'):
                item_id = add_apart(request)
            if (app_param.restriction == 'service'):
                item_id = add_service(request, apart)
            if (app_param.restriction == 'meter'):
                item_id = add_meter(request, apart)
            if (app_param.restriction == 'price'):
                item_id = add_price(request, apart)
            if (app_param.restriction == 'bill'):
                item_id = add_bill(request, apart)
            return HttpResponseRedirect(reverse('apart:item', args = [item_id]))
        if ('item-in-list-select' in request.POST) and (app_param.restriction == 'apart'):
            pk = request.POST['item-in-list-select']
            if pk:
                set_active(request.user.id, pk)
                return HttpResponseRedirect(reverse('apart:item', args = [pk]))

    app_param, context = get_base_context_ext(request, app_name, 'main', get_title(app_param.restriction, apart))

    redirect = False

    if app_param.article:
        valid_article = False
        if (app_param.restriction == 'apart'):
            valid_article = Apart.objects.filter(id = app_param.art_id, user = request.user.id).exists()
        if (app_param.restriction == 'service'):
            valid_article = Service.objects.filter(id = app_param.art_id, apart = apart.id).exists()
        if (app_param.restriction == 'meter'):
            valid_article = Meter.objects.filter(id = app_param.art_id, apart = apart.id).exists()
        if (app_param.restriction == 'price'):
            valid_article = Price.objects.filter(id = app_param.art_id, apart = apart.id).exists()
        if (app_param.restriction == 'bill'):
            valid_article = Bill.objects.filter(id = app_param.art_id, apart = apart.id).exists()
        if valid_article:
            if (app_param.restriction == 'apart'):
                item = get_object_or_404(Apart.objects.filter(id = app_param.art_id, user = request.user.id))
                disable_delete = item.active or Meter.objects.filter(apart = item.id).exists() or \
                                                Price.objects.filter(apart = item.id).exists() or \
                                                Bill.objects.filter(apart = item.id).exists()
                redirect = edit_item(request, context, app_param.restriction, None, item, disable_delete)
            if (app_param.restriction == 'meter'):
                item = get_object_or_404(Meter.objects.filter(id = app_param.art_id, apart = apart.id))
                disable_delete = Bill.objects.filter(prev = item.id).exists() or Bill.objects.filter(curr = item.id).exists()
                redirect = edit_item(request, context, app_param.restriction, apart, item, disable_delete)
            if (app_param.restriction == 'service'):
                item = get_object_or_404(Service.objects.filter(id = app_param.art_id, apart = apart.id))
                disable_delete = Price.objects.filter(serv = item.id).exists()
                redirect = edit_item(request, context, app_param.restriction, apart, item, disable_delete)
            if (app_param.restriction == 'price'):
                item = get_object_or_404(Price.objects.filter(id = app_param.art_id, apart = apart.id))
                redirect = edit_item(request, context, app_param.restriction, apart, item)
            if (app_param.restriction == 'bill'):
                item = get_object_or_404(Bill.objects.filter(id = app_param.art_id, apart = apart.id))
                disable_delete = Bill.objects.filter(period__gt = item.period).exists()
                redirect = edit_item(request, context, app_param.restriction, apart, item, disable_delete)
        else:
            set_article_visible(request.user, app_name, False)
            redirect = True
    
    if redirect:
        return HttpResponseRedirect(reverse('apart:main') + extract_get_params(request))

    fixes = []
    fixes.append(Fix('apart', _('apartments').capitalize(), 'todo/icon/myday.png', 'aparts/', len(Apart.objects.filter(user = request.user.id))))
    fixes.append(Fix('service', _('services').capitalize(), 'rok/icon/execute.png', 'services/', len(Service.objects.filter(apart = apart.id))))
    fixes.append(Fix('meter', _('meters').capitalize(), 'todo/icon/planned.png', 'meters/', len(Meter.objects.filter(apart = apart.id))))
    fixes.append(Fix('price', _('prices').capitalize(), 'rok/icon/all.png', 'prices/', len(Price.objects.filter(apart = apart.id))))
    fixes.append(Fix('bill', _('bills').capitalize(), 'todo/icon/important.png', 'bills/', len(Bill.objects.filter(apart = apart.id))))
    context['fix_list'] = fixes

    context['without_lists'] = True
    context['hide_important'] = True
    if (app_param.restriction == 'apart'):
        context['add_item_placeholder'] = _('add apartment').capitalize()
    elif (app_param.restriction == 'service'):
        context['add_item_placeholder'] = _('add service').capitalize()
        context['hide_selector'] = True
    else:
        context['hide_add_item_input'] = True
        context['hide_selector'] = True

    query = None
    page_number = 1
    if (request.method == 'GET'):
        query = request.GET.get('q')
        page_number = request.GET.get('page')
    context['search_info'] = get_search_info(query)
    data = filtered_sorted_list(request.user, app_param, apart, query)
    
    
    if (app_param.restriction == 'price'):
        groups = []
        for price in data:
            serv_id = 0
            serv_name = '<услуга не указана>'
            if price.serv and (price.serv.apart == price.apart):
                serv_id = price.serv.id
                serv_name = price.serv.name
            group = find_group(groups, request.user, app_name, serv_id, serv_name)
            group.items.append(price)
        context['item_groups'] = sorted(groups, key = lambda group: group.grp.name)
    else:
        paginator = Paginator(data, items_per_page)
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = paginator.get_page(page_number)

    template = loader.get_template('apart/' + app_param.restriction + '.html')
    return HttpResponse(template.render(context, request))


def item(request, pk):
    set_article_kind(request.user, app_name, '', pk)
    return HttpResponseRedirect(reverse('apart:main') + extract_get_params(request))

def aparts(request):
    set_restriction(request.user, app_name, 'apart')
    return HttpResponseRedirect(reverse('apart:main'))

def services(request):
    set_restriction(request.user, app_name, 'service')
    return HttpResponseRedirect(reverse('apart:main'))

def meters(request):
    set_restriction(request.user, app_name, 'meter')
    return HttpResponseRedirect(reverse('apart:main'))

def prices(request):
    set_restriction(request.user, app_name, 'price')
    return HttpResponseRedirect(reverse('apart:main'))

def bills(request):
    set_restriction(request.user, app_name, 'bill')
    return HttpResponseRedirect(reverse('apart:main'))

def toggle(request, pk):
    toggle_content_group(request.user.id, app_name, pk)
    return HttpResponseRedirect(reverse('apart:main'))

def doc(request, name):
    app_param = get_app_params(request.user, app_name)
    bill = get_object_or_404(Bill.objects.filter(id = app_param.art_id))
    path = get_file_storage_path(request.user, bill)
    try:
        fsock = open(path + name, 'rb')
        return FileResponse(fsock)
    except IOError:
        response = HttpResponseNotFound()

#----------------------------------
def get_title(restriction, apart):
    if (restriction == 'apart'):
        return _('apartments').capitalize()
    if (restriction == 'service'):
        return '{} [{}]'.format(_('services').capitalize(), apart.name)
    if (restriction == 'meter'):
        return '{} [{}]'.format(_('meters').capitalize(), apart.name)
    if (restriction == 'price'):
        return '{} [{}]'.format(_('prices').capitalize(), apart.name)
    if (restriction == 'bill'):
        return '{} [{}]'.format(_('bills').capitalize(), apart.name)
    return 'unknown restriction: ' + str(restriction)

#----------------------------------
def filtered_list(user, restriction, apart, query = None):
    if (restriction == 'apart'):
        data = Apart.objects.filter(user = user.id)
    elif (restriction == 'service'):
        data = Service.objects.filter(apart = apart.id)
    elif (restriction == 'meter'):
        data = Meter.objects.filter(apart = apart.id)
    elif (restriction == 'price'):
        data = Price.objects.filter(apart = apart.id)
    elif (restriction == 'bill'):
        data = Bill.objects.filter(apart = apart.id)
    else:
        data = []

    if not query:
        return data

    search_mode = get_search_mode(query)
    lookups = None
    if (search_mode != 1):
        return data

    if (restriction == 'apart'):
        lookups = Q(name__icontains = query) | Q(addr__icontains = query)
    elif (restriction == 'service'):
        lookups = Q(abbr__icontains = query) | Q(name__icontains = query)
    elif (restriction == 'meter'):
        lookups = Q(info__icontains = query)
    elif (restriction == 'price'):
        lookups = Q(info__icontains = query)
    elif (restriction == 'bill'):
        lookups = Q(info__icontains = query) | Q(url__icontains = query)
    else:
        return data

    return data.filter(lookups).distinct()

def filtered_sorted_list(user, app_param, apart, query):
    data = filtered_list(user, app_param.restriction, apart, query)
    if (app_param.restriction == 'apart'):
        data = data.order_by('name')
    elif (app_param.restriction == 'service'):
        data = data.order_by('name')
    elif (app_param.restriction == 'meter'):
        data = data.order_by('-period')
    elif (app_param.restriction == 'price'):
        data = data.order_by('-start')
    elif (app_param.restriction == 'bill'):
        data = data.order_by('-period')
    return data

#----------------------------------
def edit_item(request, context, restriction, apart, item, disable_delete = False):
    form = None
    if (request.method == 'POST'):
        if ('article_delete' in request.POST):
            delete_item(request, item, disable_delete)
            return True
        if ('apart-active' in request.POST):
            set_active(request.user.id, item.id)
            return True
        if ('item-save' in request.POST):
            if (restriction == 'apart'):
                form = ApartForm(request.POST, instance = item)
            elif (restriction == 'service'):
                form = ServiceForm(request.POST, instance = item)
            elif (restriction == 'meter'):
                form = MeterForm(request.POST, instance = item)
            elif (restriction == 'price'):
                form = PriceForm(apart, request.POST, instance = item)
            elif (restriction == 'bill'):
                form = BillForm(request.POST, instance = item)
            if form.is_valid():
                data = form.save(commit = False)
                if (restriction == 'apart'):
                    data.user = request.user
                else:
                    data.apart = apart
                form.save()
                return True
        if ('apart-gas' in request.POST):
            item.has_gas = not item.has_gas
            item.save()
            return True
        if ('apart-ppo' in request.POST):
            item.has_ppo = not item.has_ppo
            item.save()
            return True
        if ('url-delete' in request.POST):
            item.url = ''
            item.save()
            return True
        if ('file-upload' in request.POST):
            file_form = FileForm(request.POST, request.FILES)
            if file_form.is_valid():
                handle_uploaded_file(request.FILES['upload'], request.user, item)
                return True

    if not form:
        if (restriction == 'apart'):
            form = ApartForm(instance = item)
            context['item_active'] = item.active
            context['has_gas'] = item.has_gas
            context['has_ppo'] = item.has_ppo
        elif (restriction == 'service'):
            form = ServiceForm(instance = item)
        elif (restriction == 'meter'):
            form = MeterForm(instance = item)
        elif (restriction == 'price'):
            form = PriceForm(apart, instance = item)
        elif (restriction == 'bill'):
            form = BillForm(instance = item)

    context['form'] = form
    context['ed_item'] = item
    if (restriction == 'bill'):
        context['volume'] = { 'el': item.curr.el - item.prev.el,
                              'ga': item.curr.ga - item.prev.ga,
                              'wt': (item.curr.hw + item.curr.cw) - (item.prev.hw + item.prev.cw) }
        context['el_tar'] = get_price_info(item.apart.id, ELECTRICITY, item.curr.period.year, item.curr.period.month)
        context['gas_tar'] = get_price_info(item.apart.id, GAS, item.curr.period.year, item.curr.period.month)
        context['water_tar'] = get_price_info(item.apart.id, WATER, item.curr.period.year, item.curr.period.month)
        context['el_bill'] = count_by_tarif(item.apart.id, item.prev, item.curr, ELECTRICITY)
        context['gas_bill'] = count_by_tarif(item.apart.id, item.prev, item.curr, GAS)
        context['water_bill'] = count_by_tarif(item.apart.id, item.prev, item.curr, WATER)
        context['period_num'] = item.period.year * 100 + item.period.month
        context['files'] = get_files_list(request.user, app_name, 'apart_{}/{}/{}'.format(item.apart.id, item.period.year, str(item.period.month).zfill(2)))
    return False

#----------------------------------
def delete_item(request, item, disable_delete = False):
    if disable_delete:
        return False
    item.delete()
    set_article_visible(request.user, app_name, False)
    return True

#----------------------------------
def add_apart(request):
    item = Apart.objects.create(user = request.user, name = request.POST['item_add-name'])
    return item.id

def add_service(request, apart):
    item = Service.objects.create(apart = apart, name = request.POST['item_add-name'])
    return item.id

def add_meter(request, apart):
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

    item = Meter.objects.create(apart = apart, period = period, reading = datetime.now(), el = el, hw = hw, cw = cw, ga = ga)
    return item.id

def add_price(request, apart):
    item = Price.objects.create(apart = apart)
    return item.id

def add_bill(request, apart):
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
    item = Bill.objects.create(apart = apart, period = period, payment = datetime.now(), prev = prev, curr = curr, rate = 0)
    return item.id

#----------------------------------
def get_file_storage_path(user, bill):
    return storage_path.format(user.id) + '{}/apart_{}/{}/{}/'.format(app_name, bill.apart.id, bill.period.year, str(bill.period.month).zfill(2))

def handle_uploaded_file(f, user, bill):
    path = get_file_storage_path(user, bill)
    os.makedirs(os.path.dirname(path), exist_ok = True)
    with open(path + f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

