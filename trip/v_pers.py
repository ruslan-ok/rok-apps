from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from hier.utils import get_base_context, process_common_commands, get_param, set_article, save_last_visited
from .models import Person, Trip, set_active, enrich_context
from .forms import PersonForm

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def pers_list(request):
    if process_common_commands(request):
        return HttpResponseRedirect(reverse('trip:pers_list'))

    param = get_param(request.user, 'trip:person')

    if (request.method == 'POST'):
        if ('item-add' in request.POST):
            person = Person.objects.create(user = request.user, name = request.POST['pers_name_add'])
            return HttpResponseRedirect(reverse('trip:pers_form', args = [person.id]))
        if ('person-me' in request.POST):
            pk = request.POST['person-me']
            if pk:
                set_active(request.user.id, pk)
                return HttpResponseRedirect(reverse('trip:pers_form', args = [pk]))

    context = get_base_context(request, 0, 0, _('persons').capitalize(), 'content_list', make_tree = False, article_enabled = True)
    save_last_visited(request.user, 'trip:pers_list', 'trip', context['title'])

    redirect = False

    if (param.article_mode == 'trip:person') and param.article:
        if Person.objects.filter(id = param.article_pk, user = request.user.id).exists():
            redirect = get_pers_article(request, context, param.article_pk)
        else:
            set_article(request.user, '', 0)
            redirect = True
    
    if redirect:
        return HttpResponseRedirect(reverse('trip:pers_list'))

    enrich_context(context, param, request.user.id)
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
    set_article(request.user, 'trip:person', pk)
    return HttpResponseRedirect(reverse('trip:pers_list'))

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
    set_article(request.user, '', 0)
    return True
