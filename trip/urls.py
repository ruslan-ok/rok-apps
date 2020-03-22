from django.urls import path
from . import views

app_name = 'trip'
urlpatterns = [
    path('',               views.trip_view,  name='trip_view'),
    path('<int:pk>/',      views.trip_edit,  name='trip_edit'),
    path('count/',         views.trip_count, name='trip_count'),
    path('pers/',          views.pers_view,  name='pers_view'),
    path('pers/<int:pk>/', views.pers_edit,  name='pers_edit'),
]
