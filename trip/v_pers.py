from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from hier.utils import get_base_context_ext, process_common_commands, extract_get_params
from hier.params import set_article_visible, set_article_kind
from .models import app_name, Person, Trip, set_active, enrich_context
from .forms import PersonForm

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def pers_list(request):
    if process_common_commands(request, app_name):
        return HttpResponseRedirect(reverse('trip:pers_list') + extract_get_params(request))

    if (request.method == 'POST'):
        if ('item-add' in request.POST):
            person = Person.objects.create(user = request.user, name = request.POST['pers_name_add'])
            return HttpResponseRedirect(reverse('trip:pers_form', args = [person.id]))
        if ('person-me' in request.POST):
            pk = request.POST['person-me']
            if pk:
                set_active(request.user.id, pk)
                return HttpResponseRedirect(reverse('trip:pers_form', args = [pk]))

    app_param, context = get_base_context_ext(request, app_name, 'pers', _('persons').capitalize())

    redirect = False

    if app_param.article:
        if (app_param.kind != 'person'):
            set_article_visible(request.user, app_name, False)
            redirect = True
        elif Person.objects.filter(id = app_param.art_id, user = request.user.id).exists():
            redirect = get_pers_article(request, context, app_param.art_id)
        else:
            set_article_visible(request.user, app_name, False)
            redirect = True
    
    if redirect:
        return HttpResponseRedirect(reverse('trip:pers_list') + extract_get_params(request))

    enrich_context(context, app_param, request.user.id)
    data = Person.objects.filter(user = request.user.id).order_by('-me', 'name')
    page_number = 1
    if (request.method == 'GET'):
        page_number = request.GET.get('page')
    paginator = Paginator(data, 10)
    page_obj = paginator.get_page(page_number)
    context['page_obj'] = paginator.get_page(page_number)

    template_file = 'trip/pers_form.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def pers_form(request, pk):
    set_article_kind(request.user, app_name, 'person', pk)
    return HttpResponseRedirect(reverse('trip:pers_list') + extract_get_params(request))

#----------------------------------
def get_pers_article(request, context, pk):
    ed_person = get_object_or_404(Person.objects.filter(id = pk, user = request.user.id))
    form = None
    if (request.method == 'POST'):
        if ('article_delete' in request.POST):
            pers_delete(request, ed_person)
            return True
        if ('person-save' in request.POST):
            form = PersonForm(request.POST, instance = ed_person)
            if form.is_valid():
                data = form.save(commit = False)
                data.user = request.user
                form.save()
                return True

    if not form:
        form = PersonForm(instance = ed_person)

    context['form'] = form
    context['item_id'] = ed_person.id
    context['item_active'] = ed_person.me
    return False

#----------------------------------
def pers_delete(request, person):
    if Trip.objects.filter(driver = person.id).exists() or Trip.objects.filter(passenger = person.id).exists():
        return False

    person.delete()
    set_article_visible(request.user, app_name, False)
    return True
