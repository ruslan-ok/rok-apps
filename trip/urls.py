from django.urls import path
from . import v_pers, v_trip

app_name = 'trip'
urlpatterns = [
    path('',                  v_trip.trip_list, name='trip_list'),
    path('<int:pk>/',         v_trip.trip_form, name='trip_form'),
    path('create/',           v_trip.trip_add,  name='trip_add'),
    path('persons/',          v_pers.pers_list, name='pers_list'),
    path('persons/<int:pk>/', v_pers.pers_form, name='pers_form'),
]
