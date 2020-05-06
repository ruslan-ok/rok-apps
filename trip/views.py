from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from django.views.generic.list import ListView

from hier.utils import get_base_context
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
        context_add = get_base_context(self.request, self.kwargs['folder_id'], 0, _('trips'), 'content_list')
        context.update(context_add)
        context['trip_summary'] = trip_summary(self.request.user.id)
        return context

#----------------------------------
#              Trip Form
#----------------------------------
@login_required
@permission_required('trip.view_person')
def trip_edit(request, folder_id, content_id):
    return do_trip(request, folder_id, content_id)

#----------------------------------
#              Trip Create
#----------------------------------
@login_required(login_url='account:login')
@permission_required('trip.view_person')
def trip_add(request, folder_id):
    return do_trip(request, folder_id, 0)

#----------------------------------
#              Trip Delete
#----------------------------------
@login_required(login_url='account:login')
@permission_required('trip.view_person')
def trip_del(request, folder_id, content_id):
    Trip.objects.get(id = content_id).delete()
    return HttpResponseRedirect(reverse('trip:trip_list', args = [folder_id]))


#----------------------------------
#              Trip Recount
#----------------------------------
@login_required(login_url='account:login')
@permission_required('trip.view_person')
def trip_count(request, folder_id):
    do_count(request)
    return HttpResponseRedirect(reverse('trip:trip_list', args = [folder_id]))


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
        context_add = get_base_context(self.request, self.kwargs['folder_id'], 0, _('persons'), 'content_list')
        context.update(context_add)
        return context

#----------------------------------
#              Person Form
#----------------------------------
@login_required(login_url='account:login')
@permission_required('trip.view_person')
def pers_edit(request, folder_id, content_id):
    return do_pers(request, folder_id, content_id)

#----------------------------------
#              Person Create
#----------------------------------
@login_required(login_url='account:login')
@permission_required('trip.view_person')
def pers_add(request, folder_id):
    return do_pers(request, folder_id, 0)

#----------------------------------
#              Person Delete
#----------------------------------
@login_required(login_url='account:login')
@permission_required('trip.view_person')
def pers_del(request, folder_id, content_id):
    Person.objects.get(id = content_id).delete()
    return HttpResponseRedirect(reverse('trip:pers_list', args = [folder_id]))

