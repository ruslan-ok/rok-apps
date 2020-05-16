from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from hier.utils import get_base_context, get_folder_id
from .models import Direct, Proj
from .forms import ProjForm


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def proj_list(request):
    if not Direct.objects.filter(user = request.user.id, active = True).exists():
        return HttpResponseRedirect(reverse('proj:dirs_list'))

    direct = Direct.objects.filter(user = request.user.id, active = True).get()
    data = Proj.objects.filter(direct = direct.id).order_by('-date')
    if request.method != 'GET':
        page_number = 1
    else:
        page_number = request.GET.get('page')
    paginator = Paginator(data, 10)
    page_obj = paginator.get_page(page_number)
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, 0, _('expenses') + ' ' + direct.name, 'content_list')
    context['page_obj'] = page_obj
    template_file = 'proj/proj_list.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))

#----------------------------------
def proj_add(request):
    if (request.method == 'POST'):
        form = ProjForm(request.POST)
    else:
        form = ProjForm(initial = { 'date': datetime.now() })
    return show_page_form(request, 0, _('creating a new expense') + ' ' + direct.name, form)

#----------------------------------
def proj_form(request, pk):
    direct = get_object_or_404(Direct.objects.filter(user = request.user.id, active = True))
    data = get_object_or_404(Proj.objects.filter(id = pk, direct = direct.id))
    if (request.method == 'POST'):
        form = ProjForm(request.POST, instance = data)
    else:
        form = ProjForm(instance = data)
    return show_page_form(request, pk, _('expense') + ' ' + direct.name, form)

#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def proj_del(request, pk):
    direct = get_object_or_404(Direct.objects.filter(user = request.user.id, active = True))
    proj = get_object_or_404(Proj.objects.filter(id = pk, direct = direct.id))
    proj.delete()
    return HttpResponseRedirect(reverse('proj:proj_list'))


#----------------------------------
@login_required(login_url='account:login')
#----------------------------------
def show_page_form(request, pk, title, form):
    direct = get_object_or_404(Direct.objects.filter(user = request.user.id, active = True))
    if (request.method == 'POST'):
        if form.is_valid():
            data = form.save(commit = False)
            data.direct = direct
            form.save()
            return HttpResponseRedirect(reverse('proj:proj_list'))
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, pk, title)
    context['form'] = form
    template = loader.get_template('proj/proj_form.html')
    return HttpResponse(template.render(context, request))
