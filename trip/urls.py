from django.urls import path
from . import views

app_name = 'trip'
urlpatterns = [
    path('',                   views.TripsListView.as_view(), name='index'),
    path('<int:pk>/',          views.trip_edit,  name='trip_edit'),
    path('del/<int:pk>/',      views.trip_del,   name='trip_del'),
    path('add/',               views.trip_add,   name='trip_add'),
    path('count/',             views.trip_count, name='trip_count'),
    path('pers/',              views.PersonsListView.as_view(),  name='pers_list'),
    path('pers/<int:pk>/',     views.pers_edit,  name='pers_edit'),
    path('pers/del/<int:pk>/', views.pers_del,   name='pers_del'),
    path('pers/add/',          views.pers_add,   name='pers_add'),
]
