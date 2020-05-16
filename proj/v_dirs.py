from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from hier.utils import get_base_context, get_folder_id
from .models import Direct, deactivate_all, set_active, Proj
from .forms import DirectForm


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def dirs_list(request):
    data = Direct.objects.filter(user = request.user.id).order_by('name')
    if request.method != 'GET':
        page_number = 1
    else:
        page_number = request.GET.get('page')
    paginator = Paginator(data, 20)
    page_obj = paginator.get_page(page_number)
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, 0, _('directions'), 'content_list')
    context['page_obj'] = page_obj
    template_file = 'proj/dirs_list.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

#----------------------------------
def dirs_add(request):
    if (request.method == 'POST'):
        form = DirectForm(request.POST)
    else:
        form = DirectForm(initial = { 'name': '', 'active': False })
    return show_page_form(request, 0, _('creating a new direction'), form)

#----------------------------------
def dirs_form(request, pk):
    data = get_object_or_404(Direct.objects.filter(id = pk, user = request.user.id))
    if (request.method == 'POST'):
        form = DirectForm(request.POST, instance = data)
    else:
        form = DirectForm(instance = data)
    return show_page_form(request, pk, _('direction') + ' "' + data.name + '"', form)

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def dirs_del(request, pk):
    dir = get_object_or_404(Direct.objects.filter(id = pk, user = request.user.id))
    if Proj.objects.filter(direct = dir.id).exists():
        set_active(request.user.id, dir.id)
        return HttpResponseRedirect(reverse('proj:dirs_list'))

    if dir.active:
        if Direct.objects.filter(user = request.user.id).exclude(id = dir.id).exists():
            new_active = Direct.objects.filter(user = request.user.id).exclude(id = dir.id)[0]
            set_active(request.user.id, new_active.id)

    dir.delete()
    return HttpResponseRedirect(reverse('proj:dirs_list'))


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
            return HttpResponseRedirect(reverse('proj:dirs_list'))
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, pk, title)
    context['form'] = form
    template = loader.get_template('proj/dirs_form.html')
    return HttpResponse(template.render(context, request))
