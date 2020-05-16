from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _

from hier.models import Folder
from hier.utils import get_base_context, get_folder_id
from .models import Apart, Meter, Price, Bill, deactivate_all, set_active
from .forms import ApartForm
from .convert import convert_old_data


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def apart_param(request):
    return HttpResponseRedirect(reverse('apart:apart_list'))

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def apart_list(request):
    data = Apart.objects.filter(user = request.user.id).order_by('name')
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, 0, _('apartments'), 'content_list')
    context['page_obj'] = data
    template_file = 'apart/apart_list.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

#----------------------------------
def apart_add(request):
    if (request.method == 'POST'):
        form = ApartForm(request.POST)
    else:
        form = ApartForm(initial = { 'name': '', 'addr': '', 'active': False, 'has_gas': True })
    return show_page_form(request, 0, _('creating a new apartment'), form)

#----------------------------------
def apart_form(request, pk):
    data = get_object_or_404(Apart.objects.filter(id = pk, user = request.user.id))
    if (request.method == 'POST'):
        form = ApartForm(request.POST, instance = data)
    else:
        form = ApartForm(instance = data)
    return show_page_form(request, pk, _('apartment') + ' "' + data.name + '"', form)

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def apart_del(request, pk):
    apart = get_object_or_404(Apart.objects.filter(id = pk, user = request.user.id))
    if Communal.objects.filter(apart = apart.id).exists():
        set_active(request.user.id, apart.id)
        return HttpResponseRedirect(reverse('apart:apart_list'))

    if apart.active:
        if Apart.objects.filter(user = request.user.id).exclude(id = apart.id).exists():
            new_active = Apart.objects.filter(user = request.user.id).exclude(id = apart.id)[0]
            set_active(request.user.id, new_active.id)

    apart.delete()
    return HttpResponseRedirect(reverse('apart:apart_list'))


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def show_page_form(request, pk, title, form):
    if (request.method == 'POST'):
        if form.is_valid():
            data = form.save(commit = False)
            if data.active:
                deactivate_all(request.user.id, data.id)
            data.user = request.user
            form.save()
            if not pk and data.active and not Price.objects.all().exists():
                convert_old_data(request.user, data)
            return HttpResponseRedirect(reverse('apart:apart_list'))
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, pk, title)
    context['form'] = form
    template = loader.get_template('apart/apart_form.html')
    return HttpResponse(template.render(context, request))
