from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from hier.utils import get_base_context, process_common_commands, get_param, set_article, save_last_visited
from .models import Apart, Meter, enrich_context
from .forms import MeterForm
from .utils import next_period

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def meter_list(request):
    if process_common_commands(request):
        return HttpResponseRedirect(reverse('apart:meter_list'))

    if not Apart.objects.filter(user = request.user.id, active = True).exists():
        return HttpResponseRedirect(reverse('apart:apart_list'))
    apart = get_object_or_404(Apart.objects.filter(user = request.user.id, active = True))
    data = Meter.objects.filter(apart = apart.id).order_by('-period')

    param = get_param(request.user, 'apart:meter')

    if param.article and Meter.objects.filter(apart = apart.id, id = param.article_pk).exists():
        meter = Meter.objects.filter(apart = apart.id, id = param.article_pk).get()
        title = '{} {} {} {}'.format(_('meter readings in').capitalize(), apart.name, _('for the period'), meter.period.strftime('%m.%Y'))
    else:
        title = '{} {}'.format(_('meters in').capitalize(), apart.name)

    if (request.method == 'POST'):
        if ('item-add' in request.POST):
            meter = meter_add(request, apart)
            set_article(request.user, 'apart:meter', meter.id)
            return HttpResponseRedirect(reverse('apart:meter_form', args = [meter.id]))

    context = get_base_context(request, 0, 0, title, 'content_list', make_tree = False, article_enabled = True)
    save_last_visited(request.user, 'apart:meter_list', 'Коммуналка', context['title'])

    redirect = False
    if param.article:
        if Meter.objects.filter(id = param.article_pk, apart = apart.id).exists():
            redirect = get_meter_article(request, context, param.article_pk)
        else:
            set_article(request.user, '', 0)
            redirect = True
    
    if redirect:
        return HttpResponseRedirect(reverse('apart:meter_list'))

    enrich_context(context, param, request.user.id)
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
    set_article(request.user, 'apart:meter', pk)
    return HttpResponseRedirect(reverse('apart:meter_list'))

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
            set_article(request.user, '', 0)
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



