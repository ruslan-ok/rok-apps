# coding=UTF-8
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from trip.v_pers import do_pers
from trip.v_trip import do_trip, do_count


@login_required
def trip_view(request):
    return do_trip(request, 0)

@login_required
def trip_edit(request, pk):
    return do_trip(request, int(pk))

@login_required
def trip_count(request):
    do_count(request)
    return HttpResponseRedirect(reverse('trip:trip_view'))


@login_required
def pers_view(request):
    return do_pers(request, 0)

@login_required
def pers_edit(request, pk):
    return do_pers(request, int(pk))

