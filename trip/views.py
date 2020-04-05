from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.views.generic.list import ListView

from .v_pers import do_pers
from .v_trip import do_trip, do_count
from .models import Person, Trip, trip_summary

decorators = [login_required(login_url='account:login'), permission_required('trip.view_person')]

#----------------------------------
#              Trip List
#----------------------------------
@method_decorator(decorators, name='dispatch')
class TripsListView(ListView):

    model = Trip
    paginate_by = 20

    def get_queryset(self):
        return Trip.objects.filter(user = self.request.user.id).order_by('-year', '-week', '-modif')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('trips').capitalize()
        context['site_header'] = get_current_site(self.request).name
        context['trip_summary'] = trip_summary(self.request.user.id)
        return context

#----------------------------------
#              Trip Form
#----------------------------------
@login_required
@permission_required('trip.view_person')
def trip_edit(request, pk):
    return do_trip(request, pk)

#----------------------------------
#              Trip Create
#----------------------------------
@login_required(login_url='account:login')
@permission_required('trip.view_person')
def trip_add(request):
    return do_trip(request, 0)

#----------------------------------
#              Trip Delete
#----------------------------------
@login_required(login_url='account:login')
@permission_required('trip.view_person')
def trip_del(request, pk):
    Trip.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('trip:trip_list'))


#----------------------------------
#              Trip Recount
#----------------------------------
@login_required(login_url='account:login')
@permission_required('trip.view_person')
def trip_count(request):
    do_count(request)
    return HttpResponseRedirect(reverse('trip:trip_list'))


#----------------------------------
#              Person List
#----------------------------------
@method_decorator(decorators, name='dispatch')
class PersonsListView(ListView):

    model = Person
    paginate_by = 20

    def get_queryset(self):
        return Person.objects.filter(user = self.request.user.id).order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('persons').capitalize()
        context['site_header'] = get_current_site(self.request).name
        return context

#----------------------------------
#              Person Form
#----------------------------------
@login_required(login_url='account:login')
@permission_required('trip.view_person')
def pers_edit(request, pk):
    return do_pers(request, pk)

#----------------------------------
#              Person Create
#----------------------------------
@login_required(login_url='account:login')
@permission_required('trip.view_person')
def pers_add(request):
    return do_pers(request, 0)

#----------------------------------
#              Person Delete
#----------------------------------
@login_required(login_url='account:login')
@permission_required('trip.view_person')
def pers_del(request, pk):
    Person.objects.get(id = pk).delete()
    return HttpResponseRedirect(reverse('trip:pers_list'))

