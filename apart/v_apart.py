from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _

from hier.utils import get_base_context, process_common_commands, get_param, set_article, save_last_visited
from .models import Apart, Meter, set_active, enrich_context
from .forms import ApartForm

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def apart_list(request):
    if process_common_commands(request):
        return HttpResponseRedirect(reverse('apart:apart_list'))

    if (request.method == 'POST'):
        if ('item-add' in request.POST):
            apart = Apart.objects.create(user = request.user, name = request.POST['apart_name_add'])
            return HttpResponseRedirect(reverse('apart:apart_form', args = [apart.id]))
        if ('apart-in-list-active' in request.POST):
            set_active(request.user.id, request.POST['apart-in-list-active'])
            return HttpResponseRedirect(reverse('apart:apart_list'))

    context = get_base_context(request, 0, 0, _('apartments').capitalize(), 'content_list', make_tree = False, article_enabled = True)
    save_last_visited(request.user, 'apart:apart_list', 'apart', context['title'])

    redirect = False

    param = get_param(request.user, 'apart:apart')
    if (param.article_mode == 'apart:apart') and param.article:
        if Apart.objects.filter(id = param.article_pk, user = request.user.id).exists():
            redirect = get_apart_article(request, context, param.article_pk)
        else:
            set_article(request.user, '', 0)
            redirect = True
    
    if redirect:
        return HttpResponseRedirect(reverse('apart:apart_list'))

    enrich_context(context, param, request.user.id)
    context['page_obj'] = Apart.objects.filter(user = request.user.id).order_by('name')

    template_file = 'apart/apart_form.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def apart_form(request, pk):
    set_article(request.user, 'apart:apart', pk)
    return HttpResponseRedirect(reverse('apart:apart_list'))

#----------------------------------
def get_apart_article(request, context, pk):
    ed_apart = get_object_or_404(Apart.objects.filter(id = pk, user = request.user.id))
    form = None
    if (request.method == 'POST'):
        if ('article_delete' in request.POST):
            apart_delete(request, ed_apart)
            return HttpResponseRedirect(reverse('apart:apart_list'))
        if ('apart-active' in request.POST):
            set_active(request.user.id, pk)
            return True
        if ('apart-save' in request.POST):
            ed_apart.name = request.POST['apart_name_edit']
            ed_apart.save()
            return True
        if ('apart-addr' in request.POST):
            ed_apart.addr = request.POST['apart_addr_edit']
            ed_apart.save()
            return True
        if ('apart-gas' in request.POST):
            ed_apart.has_gas = not ed_apart.has_gas
            ed_apart.save()
            return True

    if not form:
        form = ApartForm(instance = ed_apart, prefix = 'apart_edit')

    context['form'] = form
    context['item_id'] = ed_apart.id
    context['item_active'] = ed_apart.active
    return False

#----------------------------------
def apart_delete(request, apart):
    if Meter.objects.filter(apart = apart.id).exists():
        set_active(request.user.id, apart.id)
        return False

    if apart.active:
        if Apart.objects.filter(user = request.user.id).exclude(id = apart.id).exists():
            new_active = Apart.objects.filter(user = request.user.id).exclude(id = apart.id)[0]
            set_active(request.user.id, new_active.id)

    apart.delete()
    set_article(request.user, '', 0)
    return True
