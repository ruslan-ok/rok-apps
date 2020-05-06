from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _

from hier.models import Folder
from hier.utils import get_base_context
from .models import Apart, Meter, Price, Bill, deactivate_all, set_active
from .forms import ApartForm
from .convert import convert_old_data


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def apart_param(request, folder_id):
    return HttpResponseRedirect(reverse('apart:apart_list', args = [folder_id]))

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def apart_list(request, folder_id):
    node = get_object_or_404(Folder.objects.filter(id = folder_id, user = request.user.id))
    data = Apart.objects.filter(user = request.user.id).order_by('name')
    context = get_base_context(request, folder_id, 0, _('apartments'), 'content_list')
    context['object_list'] = data
    template_file = 'apart/apart_list.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

#----------------------------------
def apart_add(request, folder_id):
    if (request.method == 'POST'):
        form = ApartForm(request.POST)
    else:
        form = ApartForm(initial = { 'name': '', 'addr': '', 'active': False, 'has_gas': True })
    return show_page_form(request, folder_id, 0, _('apartment'), form)

#----------------------------------
def apart_form(request, folder_id, pk):
    data = get_object_or_404(Apart.objects.filter(id = pk, user = request.user.id))
    if (request.method == 'POST'):
        form = ApartForm(request.POST, instance = data)
    else:
        form = ApartForm(instance = data)
    return show_page_form(request, folder_id, pk, _('apartment'), form)

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def apart_del(request, folder_id, pk):
    apart = get_object_or_404(Apart.objects.filter(id = pk, user = request.user.id))
    if Communal.objects.filter(apart = apart.id).exists():
        set_active(request.user.id, apart.id)
        return HttpResponseRedirect(reverse('apart:apart_list', args = [folder_id]))

    if apart.active:
        if Apart.objects.filter(user = request.user.id).exclude(id = apart.id).exists():
            new_active = Apart.objects.filter(user = request.user.id).exclude(id = apart.id)[0]
            set_active(request.user.id, new_active.id)

    apart.delete()
    return HttpResponseRedirect(reverse('apart:apart_list', args = [folder_id]))


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def show_page_form(request, folder_id, pk, title, form):
    if (request.method == 'POST'):
        if form.is_valid():
            data = form.save(commit = False)
            if data.active:
                deactivate_all(request.user.id, data.id)
            data.user = request.user
            form.save()
            if not pk and data.active and not Price.objects.all().exists():
                convert_old_data(request.user, data)
            return HttpResponseRedirect(reverse('apart:apart_list', args = [folder_id]))
    context = get_base_context(request, folder_id, pk, title)
    context['form'] = form
    template = loader.get_template('apart/apart_form.html')
    return HttpResponse(template.render(context, request))
