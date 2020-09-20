from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from hier.utils import get_base_context_ext, process_common_commands, extract_get_params
from hier.params import set_article_visible, set_article_kind
from .models import app_name, Apart, Meter, enrich_context
from .forms import MeterForm
from .utils import next_period

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def meter_list(request):
    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('apart:meter_list'))

    if not Apart.objects.filter(user = request.user.id, active = True).exists():
        return HttpResponseRedirect(reverse('apart:apart_list'))
    apart = get_object_or_404(Apart.objects.filter(user = request.user.id, active = True))
    data = Meter.objects.filter(apart = apart.id).order_by('-period')

    if (request.method == 'POST'):
        if ('item-add' in request.POST):
            meter = meter_add(request, apart)
            return HttpResponseRedirect(reverse('apart:meter_form', args = [meter.id]))

    title = '{} [{}]'.format(_('meters').capitalize(), apart.name)
    app_param, context = get_base_context_ext(request, app_name, 'meter', title)

    redirect = False
    
    if app_param.article:
        if (app_param.kind != 'meter'):
            set_article_visible(request.user, app_name, False)
            redirect = True
        elif Meter.objects.filter(id = app_param.art_id, apart = apart.id).exists():
            redirect = get_meter_article(request, context, app_param.art_id)
        else:
            set_article_visible(request.user, app_name, False)
            redirect = True
    
    if redirect:
        return HttpResponseRedirect(reverse('apart:meter_list'))

    enrich_context(context, app_param, request.user.id)
    page_number = 1
    if (request.method == 'GET'):
        page_number = request.GET.get('page')
    paginator = Paginator(data, 10)
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = paginator.get_page(page_number)

    template_file = 'apart/meter_form.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def meter_form(request, pk):
    set_article_kind(request.user, app_name, 'meter', pk)
    return HttpResponseRedirect(reverse('apart:meter_list') + extract_get_params(request))

#----------------------------------
def meter_add(request, apart):
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

    meter = Meter.objects.create(apart = apart, period = period, reading = datetime.now(), el = el, hw = hw, cw = cw, ga = ga)
    return meter

#----------------------------------
def get_meter_article(request, context, pk):
    ed_meter = get_object_or_404(Meter.objects.filter(id = pk))
    form = None
    if (request.method == 'POST'):
        if ('article_delete' in request.POST):
            ed_meter.delete()
            set_article_visible(request.user, app_name, False)
            return HttpResponseRedirect(reverse('apart:meter_list'))
        if ('meter-save' in request.POST):
            form = MeterForm(request.POST, instance = ed_meter)
            if form.is_valid():
                data = form.save(commit = False)
                form.save()
                return True

    if not form:
        form = MeterForm(instance = ed_meter)

    context['form'] = form
    context['item_id'] = ed_meter.id
    return False



