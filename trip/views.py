from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from trip.v_pers import do_pers
from trip.v_trip import do_trip, do_count


@login_required(login_url='account:login')
@permission_required('trip.view_person')
def trip_view(request):
    return do_trip(request, 0)

@login_required(login_url='account:login')
@permission_required('trip.view_person')
def trip_edit(request, pk):
    return do_trip(request, int(pk))

@login_required(login_url='account:login')
@permission_required('trip.view_person')
def trip_count(request):
    do_count(request)
    return HttpResponseRedirect(reverse('trip:trip_view'))


@login_required(login_url='account:login')
@permission_required('trip.view_person')
def pers_view(request):
    return do_pers(request, 0)

@login_required(login_url='account:login')
@permission_required('trip.view_person')
def pers_edit(request, pk):
    return do_pers(request, int(pk))

