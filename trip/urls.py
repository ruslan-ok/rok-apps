from django.urls import path
from . import views

app_name = 'trip'
urlpatterns = [
    path('trips/',                        views.TripsListView.as_view(), name='trip_list'),
    path('trips/create/',                 views.trip_add,   name='trip_add'),
    path('trip/<int:content_id>/',        views.trip_edit,  name='trip_edit'),
    path('trip/<int:content_id>/delete/', views.trip_del,   name='trip_del'),

    path('count/',                        views.trip_count, name='trip_count'),
                                         
    path('pers/',                         views.PersonsListView.as_view(),  name='pers_list'),
    path('pers/create/',                  views.pers_add,   name='pers_add'),
    path('pers/<int:content_id>/',        views.pers_edit,  name='pers_edit'),
    path('pers/<int:content_id>/delete/', views.pers_del,   name='pers_del'),
]
