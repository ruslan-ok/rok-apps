from django.urls import path
from . import views

app_name = 'trip'
urlpatterns = [
    path('trips/',                   views.TripsListView.as_view(), name='trip_list'),
    path('trips/create/',            views.trip_add,   name='trip_add'),
    path('trip/<int:pk>/',           views.trip_form,  name='trip_form'),
    path('trip/<int:pk>/delete/',    views.trip_del,   name='trip_del'),
                                    
    path('count/',                   views.trip_count, name='trip_count'),
                                  
    path('trips/parameters/',        views.PersonsListView.as_view(),  name='pers_list'),
    path('trips/parameters/create/', views.pers_add,   name='pers_add'),
    path('pers/<int:pk>/',           views.pers_form,  name='pers_form'),
    path('pers/<int:pk>/delete/',    views.pers_del,   name='pers_del'),
]
