from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
#from django.utils.decorators import method_decorator
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.shortcuts import get_object_or_404, render
#from django.views.generic.list import ListView
from django.core.paginator import Paginator

from hier.utils import get_base_context, get_folder_id, process_common_commands
from .v_pers import do_pers
from .v_trip import do_trip, do_count
from .models import Person, Trip, trip_summary

#decorators = [login_required(login_url='account:login')]

#----------------------------------
#              Trip List
#----------------------------------
"""
@method_decorator(decorators, name='dispatch')
class TripsListView(ListView):

    model = Trip
    paginate_by = 20

    def get_queryset(self):
        return Trip.objects.filter(user = self.request.user.id).order_by('-year', '-week', '-modif')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folder_id = get_folder_id(self.request.user.id)
        context_add = get_base_context(self.request, folder_id, 0, _('trips'), 'content_list')
        context.update(context_add)
        context['trip_summary'] = trip_summary(self.request.user.id)
        return context
"""

def trip_list(request):
    process_common_commands(request)
    data = Trip.objects.filter(user = request.user.id).order_by('-year', '-week', '-modif')
    if request.method != 'GET':
        page_number = 1
    else:
        page_number = request.GET.get('page')
    paginator = Paginator(data, 10)
    page_obj = paginator.get_page(page_number)
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, 0, _('trips'), 'content_list')
    context['page_obj'] = page_obj
    context['trip_summary'] = trip_summary(request.user.id)
    template_file = 'trip/trip_list.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))


#----------------------------------
#              Trip Form
#----------------------------------
@login_required
def trip_form(request, pk):
    return do_trip(request, pk)

#----------------------------------
#              Trip Create
#----------------------------------
@login_required(login_url='account:login')
def trip_add(request):
    return do_trip(request, 0)

#----------------------------------
#              Trip Delete
#----------------------------------
@login_required(login_url='account:login')
def trip_del(request, pk):
    Trip.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('trip:trip_list'))


#----------------------------------
#              Trip Recount
#----------------------------------
@login_required(login_url='account:login')
def trip_count(request):
    do_count(request)
    return HttpResponseRedirect(reverse('trip:trip_list'))


#----------------------------------
#              Person List
#----------------------------------
"""
@method_decorator(decorators, name='dispatch')
class PersonsListView(ListView):

    model = Person
    paginate_by = 20

    def get_queryset(self):
        return Person.objects.filter(user = self.request.user.id).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        folder_id = get_folder_id(self.request.user.id)
        context_add = get_base_context(self.request, folder_id, 0, _('persons'), 'content_list')
        context.update(context_add)
        return context
"""
def pers_list(request):
    process_common_commands(request)
    data = Person.objects.filter(user = request.user.id).order_by('name')
    if request.method != 'GET':
        page_number = 1
    else:
        page_number = request.GET.get('page')
    paginator = Paginator(data, 10)
    page_obj = paginator.get_page(page_number)
    folder_id = get_folder_id(request.user.id)
    context = get_base_context(request, folder_id, 0, _('trips'), 'content_list')
    context['page_obj'] = page_obj
    template_file = 'trip/person_list.html'
    template = loader.get_template(template_file)
    return HttpResponse(template.render(context, request))
#----------------------------------
#              Person Form
#----------------------------------
@login_required(login_url='account:login')
def pers_form(request, pk):
    return do_pers(request, pk)

#----------------------------------
#              Person Create
#----------------------------------
@login_required(login_url='account:login')
def pers_add(request):
    return do_pers(request, 0)

#----------------------------------
#              Person Delete
#----------------------------------
@login_required(login_url='account:login')
def pers_del(request, pk):
    Person.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('trip:pers_list'))

