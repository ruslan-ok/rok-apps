from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _

from hier.utils import get_base_context_ext, process_common_commands
from hier.params import set_article_visible, set_article_kind
from .models import app_name, Apart, Price, Service, enrich_context
from .forms import PriceForm
from .utils import next_period

#----------------------------------
def convert_data(apart):
    if (len(Price.objects.filter(apart = apart.id)) != 0) and (len(Service.objects.filter(apart = apart.id)) == 0):
        for price in Price.objects.filter(apart = apart.id):
            if not Service.objects.filter(apart = apart.id, abbr = price.service).exists():
                service = Service.objects.create(apart = apart, abbr = price.service, name = price.s_service())
            else:
                service = Service.objects.filter(apart = apart.id, abbr = price.service).get()
            price.serv = service
            price.start = price.period
            price.save()

#----------------------------------
class Grp():
    def __init__(self, service):
        self.service = service
        self.items = []

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def price_list(request):
    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('apart:price_list'))

    if not Apart.objects.filter(user = request.user.id, active = True).exists():
        return HttpResponseRedirect(reverse('apart:apart_list'))
    apart = get_object_or_404(Apart.objects.filter(user = request.user.id, active = True))
    convert_data(apart)
    data = Price.objects.filter(apart = apart.id).order_by('-start')

    if (request.method == 'POST'):
        if ('item-add' in request.POST):
            price = price_add(request, apart)
            return HttpResponseRedirect(reverse('apart:price_form', args = [price.id]))

    title = '{} {}'.format(_('pricess in').capitalize(), apart.name)
    app_param, context = get_base_context_ext(request, app_name, 'price', title)

    redirect = False

    if app_param.article:
        if (app_param.kind != 'price'):
            set_article_visible(request.user, app_name, False)
            redirect = True
        elif Price.objects.filter(id = app_param.art_id, apart = apart.id).exists():
            redirect = get_price_article(request, context, app_param.art_id)
        else:
            set_article_visible(request.user, app_name, False)
            redirect = True
    
    if redirect:
        return HttpResponseRedirect(reverse('apart:price_list'))

    enrich_context(context, app_param, request.user.id)

    prices_tree = []
    for price in data:
        if not price.serv:
            continue
        grp = None
        for g in prices_tree:
            if (g.service.abbr == price.service):
                grp = g
                break
        if not grp:
            grp = Grp(price.serv)
            prices_tree.append(grp)
        grp.items.append(price)
    context['object_list'] = prices_tree

    template_file = 'apart/price_form.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def price_form(request, pk):
    set_article_kind(request.user, app_name, 'price', pk)
    return HttpResponseRedirect(reverse('apart:price_list'))

#----------------------------------
def price_add(request, apart):
    price = Price.objects.create(apart = apart)
    return price

#----------------------------------
def get_price_article(request, context, pk):
    ed_price = get_object_or_404(Price.objects.filter(id = pk))
    form = None
    if (request.method == 'POST'):
        if ('article_delete' in request.POST):
            ed_price.delete()
            set_article_visible(request.user, app_name, False)
            return HttpResponseRedirect(reverse('apart:price_list'))
        if ('price-save' in request.POST):
            form = PriceForm(request.POST, instance = ed_price)
            if form.is_valid():
                data = form.save(commit = False)
                form.save()
                return True

    if not form:
        form = PriceForm(instance = ed_price)

    context['form'] = form
    context['item_id'] = ed_price.id
    return False

def service(request, pk):
    service = Service.objects.filter(id = pk).get()
    service.is_open = not service.is_open
    service.save()
    return HttpResponseRedirect(reverse('apart:price_list'))
    

