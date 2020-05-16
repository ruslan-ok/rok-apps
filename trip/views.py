from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.views.generic.list import ListView

from hier.utils import get_base_context, get_folder_id
from .v_pers import do_pers
from .v_trip import do_trip, do_count
from .models import Person, Trip, trip_summary

decorators = [login_required(login_url='account:login')]

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
        folder_id = get_folder_id(self.request.user.id)
        context_add = get_base_context(self.request, folder_id, 0, _('trips'), 'content_list')
        context.update(context_add)
        context['trip_summary'] = trip_summary(self.request.user.id)
        return context

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

